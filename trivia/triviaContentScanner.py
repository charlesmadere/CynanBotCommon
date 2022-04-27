from os import path
from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaType import TriviaType


class TriviaContentScanner():

    def __init__(
        self,
        triviaSettingsRepository: TriviaSettingsRepository,
        maxAnswerLength: int = 80,
        maxQuestionLength: int = 350,
        maxPhraseAnswerLength: int = 16,
        bannedWordsFile: str = 'CynanBotCommon/trivia/bannedWords.txt'
    ):
        if triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not utils.isValidNum(maxAnswerLength):
            raise ValueError(f'maxAnswerLength argument is malformed: \"{maxAnswerLength}\"')
        elif maxAnswerLength <= 25:
            raise ValueError(f'maxAnswerLength is too small: {maxAnswerLength}')
        elif not utils.isValidNum(maxQuestionLength):
            raise ValueError(f'maxQuestionLength argument is malformed: \"{maxQuestionLength}\"')
        elif maxQuestionLength <= 100:
            raise ValueError(f'maxQuestionLength is too small: {maxQuestionLength}')
        elif not utils.isValidNum(maxPhraseAnswerLength):
            raise ValueError(f'maxPhraseAnswerLength argument is malformed: \"{maxPhraseAnswerLength}\"')
        elif maxPhraseAnswerLength < 8:
            raise ValueError(f'maxPhraseAnswerLength is too small: {maxPhraseAnswerLength}')
        elif not utils.isValidStr(bannedWordsFile):
            raise ValueError(f'bannedWordsFile argument is malformed: \"{bannedWordsFile}\"')

        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__maxAnswerLength: int = maxAnswerLength
        self.__maxQuestionLength: int = maxQuestionLength
        self.__maxPhraseAnswerLength: int = maxPhraseAnswerLength
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

        responsesContentCode = await self.__verifyQuestionResponseCount(question)
        if responsesContentCode is not TriviaContentCode.OK:
            return responsesContentCode

        lengthsContentCode = await self.__verifyQuestionContentLengths(question)
        if lengthsContentCode is not TriviaContentCode.OK:
            return lengthsContentCode

        contentSanityCode = await self.__verifyQuestionContentSanity(question)
        if contentSanityCode is not TriviaContentCode.OK:
            return contentSanityCode

        return TriviaContentCode.OK

    async def __verifyQuestionContentLengths(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if len(question.getQuestion()) >= self.__maxQuestionLength:
            return TriviaContentCode.QUESTION_TOO_LONG

        if question.getTriviaType() is TriviaType.QUESTION_ANSWER:
            for correctAnswer in question.getCorrectAnswers():
                if len(correctAnswer) >= self.__maxPhraseAnswerLength:
                    return TriviaContentCode.ANSWER_TOO_LONG

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

    async def __verifyQuestionResponseCount(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if question.getTriviaType() is not TriviaType.MULTIPLE_CHOICE:
            return TriviaContentCode.OK

        responses = question.getResponses()
        minMultipleChoiceResponses = await self.__triviaSettingsRepository.getMinMultipleChoiceResponses()

        if not utils.hasItems(responses) or len(responses) < minMultipleChoiceResponses:
            return TriviaContentCode.TOO_FEW_MULTIPLE_CHOICE_RESPONSES

        return TriviaContentCode.OK
