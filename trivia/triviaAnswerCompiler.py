import re
from typing import List, Pattern

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaAnswerCompiler():

    def __init__(self):
        self.__answerRegEx: Pattern = re.compile(r"\w+|\d+", re.IGNORECASE)
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r"[a-z]", re.IGNORECASE)

    async def compileAnswer(self, answer: str) -> str:
        if not utils.isValidStr(answer):
            return ''

        regExResult = self.__answerRegEx.findall(answer)
        return ''.join(regExResult).lower()

    async def compileAnswers(self, answers: List[str]) -> List[str]:
        if not utils.hasItems(answers):
            return list()

        compiledAnswers: List[str] = list()

        for answer in answers:
            compiledAnswer = self.compileAnswer(answer)

            if utils.isValidStr(compiledAnswer):
                compiledAnswers.append(compiledAnswer)

        return compiledAnswers

    async def verifyIsMultipleChoiceAnswer(self, answer: str) -> bool:
        if not utils.isValidStr(answer):
            return False

        return self.__multipleChoiceAnswerRegEx.fullmatch(answer) is not None
