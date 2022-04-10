from os import path
from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode


class TriviaContentScanner():

    def __init__(
        self,
        maxAnswerLength: int = 80,
        maxQuestionLength: int = 350,
        bannedWordsFile: str = 'CynanBotCommon/trivia/bannedWords.txt'
    ):
        if not utils.isValidNum(maxAnswerLength):
            raise ValueError(f'maxAnswerLength argument is malformed: \"{maxAnswerLength}\"')
        elif maxAnswerLength <= 25:
            raise ValueError(f'maxAnswerLength is too small: {maxAnswerLength}')
        elif not utils.isValidNum(maxQuestionLength):
            raise ValueError(f'maxQuestionLength argument is malformed: \"{maxQuestionLength}\"')
        elif maxQuestionLength <= 100:
            raise ValueError(f'maxQuestionLength is too small: {maxQuestionLength}')
        elif not utils.isValidStr(bannedWordsFile):
            raise ValueError(f'bannedWordsFile argument is malformed: \"{bannedWordsFile}\"')

        self.__maxAnswerLength: int = maxAnswerLength
        self.__maxQuestionLength: int = maxQuestionLength
        self.__bannedWordsFile: str = bannedWordsFile

    async def __readBannedWordsList(self) -> List[str]:
        if not path.exists(self.__bannedWordsFile):
            raise FileNotFoundError(f'Banned Words file not found: \"{self.__bannedWordsFile}\"')

        with open(self.__bannedWordsFile, 'r') as file:
            lines = file.readlines()

        bannedWords: List[str] = list()

        if utils.hasItems(lines):
            for line in lines:
                if utils.isValidStr(line):
                    line = line.strip().lower()
                    bannedWords.append(line)

        if utils.hasItems(bannedWords):
            return bannedWords
        else:
            return None

    async def verify(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if question is None:
            return TriviaContentCode.IS_NONE

        lengthsContentCode = await self.__verifyQuestionContentLengths(question)
        if lengthsContentCode is not TriviaContentCode.OK:
            return lengthsContentCode

        return await self.__verifyQuestionContentSanity(question)

    async def __verifyQuestionContentLengths(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if len(question.getQuestion()) >= self.__maxQuestionLength:
            return TriviaContentCode.QUESTION_TOO_LONG

        for response in question.getResponses():
            if len(response) >= self.__maxAnswerLength:
                return TriviaContentCode.ANSWER_TOO_LONG

        return TriviaContentCode.OK

    async def __verifyQuestionContentSanity(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        strings: List[str] = list()
        strings.append(question.getQuestion().lower())
        strings.append(question.getPrompt().lower())

        for response in question.getResponses():
            strings.append(response.lower())

        bannedWords = await self.__readBannedWordsList()

        for string in strings:
            if not utils.isValidStr(string):
                return TriviaContentCode.CONTAINS_EMPTY_STR
            elif utils.containsUrl(string):
                return TriviaContentCode.CONTAINS_URL
            elif utils.hasItems(bannedWords):
                for bannedWord in bannedWords:
                    if bannedWord in string:
                        return TriviaContentCode.CONTAINS_BANNED_WORD

        return TriviaContentCode.OK
