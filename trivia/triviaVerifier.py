try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaContentScanner import TriviaContentScanner
    from CynanBotCommon.trivia.triviaHistoryRepository import \
        TriviaHistoryRepository
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaHistoryRepository import TriviaHistoryRepository
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaType import TriviaType


class TriviaVerifier():

    def __init__(
        self,
        triviaContentScanner: TriviaContentScanner,
        triviaHistoryRepository: TriviaHistoryRepository,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if triviaContentScanner is None:
            raise ValueError(f'triviaContentScanner argument is malformed: \"{triviaContentScanner}\"')
        elif triviaHistoryRepository is None:
            raise ValueError(f'triviaHistoryRepository argument is malformed: \"{triviaHistoryRepository}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__triviaContentScanner: TriviaContentScanner = triviaContentScanner
        self.__triviaHistoryRepository: TriviaHistoryRepository = triviaHistoryRepository
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

    async def verify(self, question: AbsTriviaQuestion, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if question is None:
            return TriviaContentCode.IS_NONE

        if question.getTriviaType() is TriviaType.MULTIPLE_CHOICE:
            responses = question.getResponses()
            minMultipleChoiceResponses = self.__triviaSettingsRepository.getMinMultipleChoiceResponses()

            if not utils.hasItems(responses) or len(responses) < minMultipleChoiceResponses:
                return TriviaContentCode.TOO_FEW_MULTIPLE_CHOICE_RESPONSES

        contentScannerCode = await self.__triviaContentScanner.verify(question)
        if contentScannerCode is not TriviaContentCode.OK:
            return contentScannerCode

        historyRepositoryCode = await self.__triviaHistoryRepository.verify(question, twitchChannel)
        if historyRepositoryCode is not TriviaContentCode.OK:
            return historyRepositoryCode

        return TriviaContentCode.OK
