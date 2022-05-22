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
        self.__numberToWordMap: Dict[str, str] = self.__getNumberToWordMap()
        self.__wordToNumberMap: Dict[str, str] = self.__getWordToNumberMap()
        self.__prefixStringsToRemove: List[str] = [ 'a ', 'an ', 'and ', 'or ', 'the ' ]
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r'[a-z]', re.IGNORECASE)
        self.__parenGroupRegEx: Pattern = re.compile(r'(\(.*?\))', re.IGNORECASE)
        self.__phraseAnswerRegEx: Pattern = re.compile(r'[^A-Za-z0-9 ]|(?<=\s)\s+', re.IGNORECASE)
        self.__tagRemovalRegEx: Pattern = re.compile(r'<\/?\w+>', re.IGNORECASE)
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s\s*', re.IGNORECASE)

    async def compileBoolAnswer(self, answer: str) -> str:
        cleanedAnswer = await self.compileTextAnswer(answer)

        try:
            return utils.strToBool(cleanedAnswer)
        except ValueError:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to bool (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

    async def compileTextAnswer(self, answer: str) -> str:
        if not utils.isValidStr(answer):
            return ''

        answer = answer.strip().lower()
        answer = self.__tagRemovalRegEx.sub('', answer)
        answer = answer.replace(' & ', ' and ')

        for prefixString in self.__prefixStringsToRemove:
            if answer.startswith(prefixString) and len(answer) > len(prefixString):
                answer = answer[len(prefixString):]
                break

        return self.__phraseAnswerRegEx.sub('', answer)

    async def compileTextAnswerToMultipleChoiceOrdinal(self, answer: str) -> int:
        cleanedAnswer = await self.compileTextAnswer(answer)

        if not utils.isValidStr(cleanedAnswer) or len(cleanedAnswer) != 1 or self.__multipleChoiceAnswerRegEx.fullmatch(cleanedAnswer) is None:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to multiple choice ordinal (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        return ord(cleanedAnswer.upper()) % 65

    async def compileTextAnswers(self, answers: List[str]) -> List[str]:
        if not utils.hasItems(answers):
            return list()

        cleanedAnswers: Set[str] = set()

        for answer in answers:
            possibilities = await self.__getPossibilities(answer)

            for possibility in possibilities:
                cleanedAnswer = await self.compileTextAnswer(possibility)

                if utils.isValidStr(cleanedAnswer):
                    cleanedAnswers.add(cleanedAnswer)

        return list(cleanedAnswers)

    async def __getDigitPossibilities(self, answer: str) -> List[str]:
        # TODO
        return list()

    def __getNumberToWordMap(self) -> Dict[str, str]:
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

        return numbers

    def __getWordToNumberMap(self) -> Dict[str, str]:
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

        return words

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
