try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaContentScanner import TriviaContentScanner
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
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
    from trivia.triviaFetchOptions import TriviaFetchOptions
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

    async def verify(self, question: AbsTriviaQuestion, triviaFetchOptions: TriviaFetchOptions) -> bool:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        if question is None:
            return TriviaContentCode.IS_NONE

        if question.getTriviaType() is TriviaType.MULTIPLE_CHOICE:
            if triviaFetchOptions.requireQuestionAnswerTriviaQuestion():
                return TriviaContentCode.ILLEGAL_TRIVIA_TYPE

            responses = question.getResponses()
            minMultipleChoiceResponses = await self.__triviaSettingsRepository.getMinMultipleChoiceResponses()

            if not utils.hasItems(responses) or len(responses) < minMultipleChoiceResponses:
                return TriviaContentCode.TOO_FEW_MULTIPLE_CHOICE_RESPONSES

        if question.getTriviaType() is TriviaType.QUESTION_ANSWER and not triviaFetchOptions.areQuestionAnswerTriviaQuestionsEnabled():
            return TriviaContentCode.ILLEGAL_TRIVIA_TYPE

        if question.getTriviaType() is not TriviaType.QUESTION_ANSWER and triviaFetchOptions.requireQuestionAnswerTriviaQuestion():
            return TriviaContentCode.ILLEGAL_TRIVIA_TYPE

        contentScannerCode = await self.__triviaContentScanner.verify(question)
        if contentScannerCode is not TriviaContentCode.OK:
            return contentScannerCode

        historyRepositoryCode = await self.__triviaHistoryRepository.verify(question, triviaFetchOptions.getTwitchChannel())
        if historyRepositoryCode is not TriviaContentCode.OK:
            return historyRepositoryCode

        return TriviaContentCode.OK
