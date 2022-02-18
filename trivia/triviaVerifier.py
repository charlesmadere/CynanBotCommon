try:
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaContentScanner import TriviaContentScanner
    from CynanBotCommon.trivia.triviaHistoryRepository import \
        TriviaHistoryRepository
except:
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaHistoryRepository import TriviaHistoryRepository


class TriviaVerifier():

    def __init__(
        self,
        triviaContentScanner: TriviaContentScanner,
        triviaHistoryRepository: TriviaHistoryRepository
    ):
        if triviaContentScanner is None:
            raise ValueError(f'triviaContentScanner argument is malformed: \"{triviaContentScanner}\"')
        elif triviaHistoryRepository is None:
            raise ValueError(f'triviaHistoryRepository argument is malformed: \"{triviaHistoryRepository}\"')

        self.__triviaContentScanner: TriviaContentScanner = triviaContentScanner
        self.__triviaHistoryRepository: TriviaHistoryRepository = triviaHistoryRepository

    def verify(self, question: AbsTriviaQuestion) -> bool:
        if question is None:
            return TriviaContentCode.IS_NONE

        contentScannerCode = self.__triviaContentScanner.verify(question)
        if contentScannerCode is not TriviaContentCode.OK:
            return contentScannerCode

        historyRepositoryCode = self.__triviaHistoryRepository.verify(question)
        if historyRepositoryCode is not TriviaContentCode.OK:
            return historyRepositoryCode

        return TriviaContentCode.OK
