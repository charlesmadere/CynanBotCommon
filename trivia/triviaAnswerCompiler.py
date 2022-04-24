import re
from typing import List, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaExceptions import BadTriviaAnswerException
except:
    import utils

    from trivia.triviaExceptions import BadTriviaAnswerException


class TriviaAnswerCompiler():

    def __init__(self):
        self.__answerRegEx: Pattern = re.compile(r"\w+|\d+", re.IGNORECASE)
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r"[a-z]", re.IGNORECASE)

    async def compileBoolAnswer(self, answer: str) -> str:
        cleanedAnswer = await self.compileTextAnswer(answer)

        try:
            return utils.strToBool(cleanedAnswer)
        except ValueError:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to bool (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

    async def compileTextAnswer(self, answer: str) -> str:
        if not utils.isValidStr(answer):
            return ''

        regExResult = self.__answerRegEx.findall(answer)
        return ''.join(regExResult).lower()

    async def compileTextAnswerToMultipleChoiceOrdinal(self, answer: str) -> int:
        cleanedAnswer = await self.compileTextAnswer(answer)

        if not utils.isValidStr(cleanedAnswer) or len(cleanedAnswer) != 1 or self.__multipleChoiceAnswerRegEx.fullmatch(cleanedAnswer) is None:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to multiple choice ordinal (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        return ord(cleanedAnswer.upper()) % 65

    async def compileTextAnswers(self, answers: List[str]) -> List[str]:
        if not utils.hasItems(answers):
            return list()

        cleanedAnswers: List[str] = list()

        for answer in answers:
            cleanedAnswer = await self.compileTextAnswer(answer)

            if utils.isValidStr(cleanedAnswer):
                cleanedAnswers.append(cleanedAnswer)

        return cleanedAnswers
