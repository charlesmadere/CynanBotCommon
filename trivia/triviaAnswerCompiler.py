import re
from typing import Dict, List, Pattern, Set

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
        self.__tagRemovalRegEx: Pattern = re.compile(r'<\/?\w+>', re.IGNORECASE)
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s\s*', re.IGNORECASE)

        self.__numberToWordMap: Dict[str, str] = self.__createNumberToWordMap()
        self.__wordToNumberMap: Dict[str, str] = self.__createWordToNumberMap()

        self.__ordinalToWordMap: Dict[str, str] = self.__createOrdinalToWordMap()
        self.__wordToOrdinalMap: Dict[str, str] = self.__createWordToOrdinalMap()

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

            loweredAnswer = answer.lower()

            if loweredAnswer in self.__numberToWordMap:
                cleanedAnswers.add(loweredAnswer)
                cleanedAnswers.add(self.__numberToWordMap[loweredAnswer])
            elif loweredAnswer in self.__wordToNumberMap:
                cleanedAnswers.add(loweredAnswer)
                cleanedAnswers.add(self.__wordToNumberMap[loweredAnswer])
            elif loweredAnswer in self.__ordinalToWordMap:
                cleanedAnswers.add(loweredAnswer)
                cleanedAnswers.add(self.__ordinalToWordMap[loweredAnswer])
            elif loweredAnswer in self.__wordToOrdinalMap:
                cleanedAnswers.add(loweredAnswer)
                cleanedAnswers.add(self.__wordToOrdinalMap[loweredAnswer])
            else:
                possibilities = await self.__getPossibilities(answer)

                for possibility in possibilities:
                    cleanedAnswer = await self.compileTextAnswer(possibility)

                    if utils.isValidStr(cleanedAnswer):
                        cleanedAnswers.add(cleanedAnswer)

        return list(cleanedAnswers)

    async def compileTextAnswerToMultipleChoiceOrdinal(self, answer: str) -> int:
        cleanedAnswer = await self.compileTextAnswer(answer)

        if not utils.isValidStr(cleanedAnswer) or len(cleanedAnswer) != 1 or self.__multipleChoiceAnswerRegEx.fullmatch(cleanedAnswer) is None:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to multiple choice ordinal (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        return ord(cleanedAnswer.upper()) % 65

    def __createNumberToWordMap(self) -> Dict[str, str]:
        numbers: Dict[str, str] = dict()
        numbers['0'] = 'zero'
        numbers['1'] = 'one'
        numbers['2'] = 'two'
        numbers['3'] = 'three'
        numbers['4'] = 'four'
        numbers['5'] = 'five'
        numbers['6'] = 'six'
        numbers['7'] = 'seven'
        numbers['8'] = 'eight'
        numbers['9'] = 'nine'
        numbers['10'] = 'ten'
        numbers['11'] = 'eleven'
        numbers['12'] = 'twelve'
        numbers['13'] = 'thirteen'
        numbers['14'] = 'fourteen'
        numbers['15'] = 'fifteen'
        numbers['16'] = 'sixteen'
        numbers['17'] = 'seventeen'
        numbers['18'] = 'eighteen'
        numbers['19'] = 'nineteen'
        numbers['20'] = 'twenty'

        return numbers

    def __createOrdinalToWordMap(self) -> Dict[str, str]:
        ordinals: Dict[str, str] = dict()
        ordinals['first'] = '1st'
        ordinals['second'] = '2nd'
        ordinals['third'] = '3rd'
        ordinals['fourth'] = '4th'
        ordinals['fifth'] = '5th'
        ordinals['sixth'] = '6th'
        ordinals['seventh'] = '7th'
        ordinals['eighth'] = '8th'
        ordinals['ninth'] = '9th'
        ordinals['tenth'] = '10th'

        return ordinals

    def __createWordToNumberMap(self) -> Dict[str, str]:
        words: Dict[str, str] = dict()
        words['zero'] = '0'
        words['one'] = '1'
        words['two'] = '2'
        words['three'] = '3'
        words['four'] = '4'
        words['five'] = '5'
        words['six'] = '6'
        words['seven'] = '7'
        words['eight'] = '8'
        words['nine'] = '9'
        words['ten'] = '10'
        words['eleven'] = '11'
        words['twelve'] = '12'
        words['thirteen'] = '13'
        words['fourteen'] = '14'
        words['fifteen'] = '15'
        words['sixteen'] = '16'
        words['seventeen'] = '17'
        words['eighteen'] = '18'
        words['nineteen'] = '19'
        words['twenty'] = '20'

        return words

    def __createWordToOrdinalMap(self) -> Dict[str, str]:
        ordinals: Dict[str, str] = dict()
        ordinals['1st'] = 'first'
        ordinals['2nd'] = 'second'
        ordinals['3rd'] = 'third'
        ordinals['4th'] = 'fourth'
        ordinals['5th'] = 'fifth'
        ordinals['6th'] = 'sixth'
        ordinals['7th'] = 'seventh'
        ordinals['8th'] = 'eighth'
        ordinals['9th'] = 'ninth'
        ordinals['10th'] = 'tenth'

        return ordinals

    # Returns all possibilities with parenthesized phrases both included and excluded
    async def __getPossibilities(self, answer: str) -> List[str]:
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
