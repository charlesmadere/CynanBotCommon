from typing import List, Optional, Set

import aiofiles
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaType import TriviaType


class TriviaContentScanner():

    def __init__(
        self,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        bannedWordsFile: str = 'CynanBotCommon/trivia/bannedWords.txt'
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not utils.isValidStr(bannedWordsFile):
            raise ValueError(f'bannedWordsFile argument is malformed: \"{bannedWordsFile}\"')

        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__bannedWordsFile: str = bannedWordsFile

        self.__bannedWordsCache: Optional[List[str]] = None

    async def clearCaches(self):
        self.__bannedWordsCache = None
        self.__timber.log('TriviaContentScanner', 'Caches cleared')

    async def __readBannedWordsList(self) -> List[str]:
        if self.__bannedWordsCache:
            return self.__bannedWordsCache

        bannedWordsSet: Set[str] = set()

        if await aiofiles.ospath.exists(self.__bannedWordsFile):
            lines: Optional[List[str]] = None

            async with aiofiles.open(self.__bannedWordsFile, 'r') as file:
                lines = await file.readlines()

            if utils.hasItems(lines):
                for line in lines:
                    if utils.isValidStr(line):
                        line = line.strip().lower()

                        if utils.isValidStr(line):
                            bannedWordsSet.add(line)

            self.__timber.log('TriviaContentScanner' f'Read in {len(bannedWordsSet)} banned word(s) from \"{self.__bannedWordsFile}\"')
        else:
            self.__timber.log('TriviaContentScanner', f'Not attempting to read in any banned words due to the file missing: \"{self.__bannedWordsFile}\"')

        bannedWordsList = list(bannedWordsSet)
        self.__bannedWordsCache = bannedWordsList
        return bannedWordsList

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
        maxQuestionLength = await self.__triviaSettingsRepository.getMaxQuestionLength()

        if len(question.getQuestion()) >= maxQuestionLength:
            self.__timber.log('TriviaContentScanner', f'Trivia question is too long (max is {maxQuestionLength}): {question.getQuestion()}')
            return TriviaContentCode.QUESTION_TOO_LONG

        maxPhraseAnswerLength = await self.__triviaSettingsRepository.getMaxPhraseAnswerLength()

        if question.getTriviaType() is TriviaType.QUESTION_ANSWER:
            for correctAnswer in question.getCorrectAnswers():
                if len(correctAnswer) >= maxPhraseAnswerLength:
                    self.__timber.log('TriviaContentScanner', f'Trivia answer is too long (max is {maxPhraseAnswerLength}): {question.getCorrectAnswers()}')
                    return TriviaContentCode.ANSWER_TOO_LONG

        maxAnswerLength = await self.__triviaSettingsRepository.getMaxAnswerLength()

        for response in question.getResponses():
            if len(response) >= maxAnswerLength:
                self.__timber.log('TriviaContentScanner', f'Trivia response is too long (max is {maxAnswerLength}): {question.getResponses()}')
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
                self.__timber.log('TriviaContentScanner', f'Trivia content contains an empty string: \"{string}\"')
                return TriviaContentCode.CONTAINS_EMPTY_STR
            elif utils.containsUrl(string):
                self.__timber.log('TriviaContentScanner', f'Trivia content contains a URL: \"{string}\"')
                return TriviaContentCode.CONTAINS_URL
            elif utils.hasItems(bannedWords):
                for bannedWord in bannedWords:
                    if bannedWord in string:
                        self.__timber.log('TriviaContentScanner', f'Trivia content contains a banned word ({bannedWord}): \"{string}\"')
                        return TriviaContentCode.CONTAINS_BANNED_WORD

        return TriviaContentCode.OK

    async def __verifyQuestionResponseCount(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if question.getTriviaType() is not TriviaType.MULTIPLE_CHOICE:
            return TriviaContentCode.OK

        responses = question.getResponses()
        minMultipleChoiceResponses = await self.__triviaSettingsRepository.getMinMultipleChoiceResponses()

        if not utils.hasItems(responses) or len(responses) < minMultipleChoiceResponses:
            self.__timber.log('TriviaContentScanner', f'Trivia question has too few multiple choice responses (min is {minMultipleChoiceResponses}): {responses}')
            return TriviaContentCode.TOO_FEW_MULTIPLE_CHOICE_RESPONSES

        return TriviaContentCode.OK
