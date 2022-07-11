import re
from typing import Dict, List, Pattern, Set, Generator
import roman
from num2words import num2words

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaExceptions import BadTriviaAnswerException
except:
    import utils

    from trivia.triviaExceptions import BadTriviaAnswerException


class TriviaAnswerCompiler():

    def __init__(self):
        self.__ampersandRegEx: Pattern = re.compile(r'(^&\s+)|(\s+&\s+)|(\s+&$)', re.IGNORECASE)
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r'[a-z]', re.IGNORECASE)
        self.__newLineRegEx: Pattern = re.compile(r'(\n)+', re.IGNORECASE)
        self.__parenGroupRegEx: Pattern = re.compile(r'(\(.*?\))', re.IGNORECASE)
        self.__phraseAnswerRegEx: Pattern = re.compile(r'[^A-Za-z0-9 ]|(?<=\s)\s+', re.IGNORECASE)
        self.__prefixRegEx: Pattern = re.compile(r'^(a|an|and|or|the)\s+', re.IGNORECASE)
        self.__tagRemovalRegEx: Pattern = re.compile(r'[<\[]\/?\w+[>\]]', re.IGNORECASE)
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s\s*', re.IGNORECASE)

        # RegEx pattern for arabic and roman numerals, returning only one capturing group
        self.__numeralRegEx = re.compile(r'\b(\d+(?:st|nd|rd|th)?|[IVXLCDM]+(?:st|nd|rd|th)?)\b', re.IGNORECASE)
        # RegEx patterns for arabic and roman numerals, returning separate capturing groups for digits and ordinals
        self.__groupedNumeralRegEx = re.compile(r'\b(?:(\d+)|([IVXLCDM]+))(st|nd|rd|th)?\b', re.IGNORECASE)

        self.__irregular_nouns = {
            'child': 'children',
            'goose': 'geese',
            'man': 'men',
            'woman': 'women',
            'person': 'people',
            'tooth': 'teeth',
            'foot': 'feet',
            'mouse': 'mice',
            'die': 'dice',
            'ox': 'oxen',
            'index': 'indices',
        }

        self.stopwords = (
            'i', 'me', 'my', 'myself', 'we', 'ourselves', 'you', 'he', 'him', 'his', 'she', 'they', 'them',  'what',
            'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now',
        )

    async def compileBoolAnswer(self, answer: str) -> str:
        cleanedAnswer = await self.compileTextAnswer(answer)

        try:
            return utils.strToBool(cleanedAnswer)
        except ValueError:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to bool (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

    async def compileTextAnswer(self, answer: str) -> str:
        if not utils.isValidStr(answer):
            return ''

        answer = answer.lower().strip()

        # removes HTML tag-like junk
        answer = self.__tagRemovalRegEx.sub('', answer).strip()

        # replaces all new line characters with just a space
        answer = self.__newLineRegEx.sub(' ', answer).strip()

        # removes common phrase prefixes
        answer = self.__prefixRegEx.sub('', answer).strip()

        # replaces the '&' character, when used like the word "and", with the word "and"
        answer = self.__ampersandRegEx.sub(' and ', answer).strip()

        # removes all special characters
        answer = self.__phraseAnswerRegEx.sub('', answer).strip()

        return answer

    async def compileTextAnswersList(self, answers: List[str]) -> List[str]:
        if not utils.hasItems(answers):
            return list()

        cleanedAnswers: Set[str] = set()

        for answer in answers:
            if not utils.isValidStr(answer):
                continue

            possibilities = await self.__getParentheticalPossibilities(answer)

            for possibility in possibilities:
                cleanedAnswer = await self.compileTextAnswer(possibility)
                cleanedAnswers.add(cleanedAnswer)

        return list(answer for answer in cleanedAnswers if utils.isValidStr(answer))

    # returns text answers with all arabic and roman numerals expanded into possible full-word forms
    async def expandNumerals(self, answer: str) -> Generator[List[str], None, None]:
        split = self.__numeralRegEx.split(answer)
        for i in range(1, len(split), 2):
            match = self.__groupedNumeralRegEx.fullmatch(split[i])
            if not match:
                raise BadTriviaAnswerException(f'numbers cannot be expanded properly in trivia answer (answer: {answer})')
            if not match.group(1):
                # roman numerals
                split[i] = await self.__getRomanNumeralSubstitutes(match.group(2), len(match.group(3) or '') > 1)
            else:
                # arabic numerals
                split[i] = await self.__getArabicNumeralSubstitutes(match.group(1), len(match.group(3) or '') > 1)
        return list(set(''.join(item) for item in utils.permuteSubArrays(split)))

    async def compileTextAnswerToMultipleChoiceOrdinal(self, answer: str) -> int:
        cleanedAnswer = await self.compileTextAnswer(answer)

        if not utils.isValidStr(cleanedAnswer) or len(cleanedAnswer) != 1 or self.__multipleChoiceAnswerRegEx.fullmatch(cleanedAnswer) is None:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to multiple choice ordinal (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        return ord(cleanedAnswer.upper()) % 65

    async def __getArabicNumeralSubstitutes(self, arabicNumerals, isDefinitelyOrdinal=False):
        individualDigits = ' '.join([num2words(int(digit)) for digit in arabicNumerals])
        n = int(arabicNumerals)
        if isDefinitelyOrdinal:
            # has ordinal suffix
            return [
                num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                'the ' + num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                individualDigits,
            ]
        else:
            return [
                num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                'the ' + num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                num2words(n).replace('-', ' ').replace(',', ''),
                num2words(n, to='year').replace('-', ' ').replace(',', ''),
                individualDigits,
            ]

    async def __getRomanNumeralSubstitutes(self, romanNumerals, isDefinitelyOrdinal=False):
        n = roman.fromRoman(romanNumerals)
        if isDefinitelyOrdinal:
            return [
                num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                'the ' + num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
            ]
        else:
            return [
                num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                'the ' + num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                num2words(n).replace('-', ' ').replace(',', ''),
                num2words(n, to='year').replace('-', ' ').replace(',', ''),
            ]

    def __genPluralPossibilities(self, word: str) -> List[str]:
        # don't preprocess stopwords
        if word in self.stopwords:
            yield word
        else:
            # TODO: return all variants of this word that we should consider valid (pluralization, etc.)
            #   (number->word expansions etc should be done way earlier, not here)
            yield word
            # pluralizations
            if any(word.endswith(s) for s in ('ss', 'sh', 'ch', 'x', 'z', 's', 'o')):
                yield word+'es'
            if word[-1] in 'sz':
                yield word + word[-1] + 'es'
            elif word.endswith('f'):
                yield word[:-1] + 'ves'
            elif word.endswith('fe'):
                yield word[:-2] + 'ves'
            elif word[-1] == 'y' and len(word) > 1 and word[-2] not in 'aeiou':
                yield word[:-1] + 'ies'
            elif word.endswith('us'):
                yield word[:-2] + 'i'
            elif word.endswith('is'):
                yield word[:-2] + 'es'
            elif word.endswith('on') or word.endswith('um'):
                yield word[:-2] + 'a'
            if word in self.__irregular_nouns:
                yield self.__irregular_nouns[word]
            if word[-1] != 's':
                yield word + 's'

    def __genMergedWords(self, words, target_length):
        if len(words) <= target_length:
            yield words
        else:
            for i in range(len(words) - 1):
                # merge the ith and i+1th word
                w = words[:]
                p = w.pop(i+1)
                w[i] += p
                # recurse on the new merged set until target length is reached
                yield from self.__mergeWords_generator(w, target_length)

    # Returns all possibilities with parenthesized phrases both included and excluded
    async def __getParentheticalPossibilities(self, answer: str) -> List[str]:
        # Split the uncleaned answer with this regex to find all parentheticals
        splitPossibilities = self.__parenGroupRegEx.split(answer)

        # join the split possibilities back to strings and substitute multiple whitespaces back to a single space.
        return [ self.__whiteSpaceRegEx.sub(' ', ''.join(p).strip()) for p in await self.__getSubPossibilities(splitPossibilities) ]

    # Recursively resolves the possibilities for each word in the answer.
    async def __getSubPossibilities(self, splitAnswer: str) -> List[str]:
        # early exit on trivial cases
        if not len(splitAnswer):
            return [ ]
        if len(splitAnswer) == 1:
            return [ splitAnswer ]

        # get all "future" possible variants starting with the next word
        futurePossible = await self.__getSubPossibilities(splitAnswer[1:])

        # switch on open paren
        if splitAnswer[0].startswith('('):
            res = [ ]
            for possible in futurePossible:
                # add a version including this word but without the parentheses
                res.append([ splitAnswer[0][1:-1], *possible ])
                # also keep the version not including this word at all
                res.append(possible)
            # return all possibilities, with and without this word
            return res
        else:
            # return all future possibilities with this current word mapped onto it as well.
            return [ [ splitAnswer[0], *possible ] for possible in futurePossible ]
