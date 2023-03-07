from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.bannedTriviaIdsRepository import \
        BannedTriviaIdsRepository
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaContentScanner import TriviaContentScanner
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaHistoryRepository import \
        TriviaHistoryRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.bannedTriviaIdsRepository import BannedTriviaIdsRepository
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaHistoryRepository import TriviaHistoryRepository
    from trivia.triviaType import TriviaType


class TriviaVerifier():

    def __init__(
        self,
        bannedTriviaIdsRepository: BannedTriviaIdsRepository,
        timber: Timber,
        triviaContentScanner: TriviaContentScanner,
        triviaHistoryRepository: TriviaHistoryRepository
    ):
        if not isinstance(bannedTriviaIdsRepository, BannedTriviaIdsRepository):
            raise ValueError(f'bannedTriviaIdsRepository argument is malformed: \"bannedTriviaIdsRepository\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaContentScanner, TriviaContentScanner):
            raise ValueError(f'triviaContentScanner argument is malformed: \"{triviaContentScanner}\"')
        elif not isinstance(triviaHistoryRepository, TriviaHistoryRepository):
            raise ValueError(f'triviaHistoryRepository argument is malformed: \"{triviaHistoryRepository}\"')

        self.__bannedTriviaIdsRepository: BannedTriviaIdsRepository = bannedTriviaIdsRepository
        self.__timber: Timber = timber
        self.__triviaContentScanner: TriviaContentScanner = triviaContentScanner
        self.__triviaHistoryRepository: TriviaHistoryRepository = triviaHistoryRepository

    async def verify(
        self,
        question: Optional[AbsTriviaQuestion],
        emote: str,
        triviaFetchOptions: TriviaFetchOptions
    ) -> TriviaContentCode:
        if question is not None and not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidStr(emote):
            raise ValueError(f'emote argument is malformed: \"{emote}\"')
        elif not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        if question is None:
            return TriviaContentCode.IS_NONE

        if not triviaFetchOptions.areQuestionAnswerTriviaQuestionsEnabled() and question.getTriviaType() is TriviaType.QUESTION_ANSWER:
            self.__timber.log('TriviaVerifier', f'The given TriviaType is illegal: {question.getTriviaType()} (triviaFetchOptions: {triviaFetchOptions.toStr()})')
            return TriviaContentCode.ILLEGAL_TRIVIA_TYPE
        elif triviaFetchOptions.requireQuestionAnswerTriviaQuestion() and question.getTriviaType() is not TriviaType.QUESTION_ANSWER:
            self.__timber.log('TriviaVerifier', f'The given TriviaType is illegal: {question.getTriviaType()} (triviaFetchOptions: {triviaFetchOptions.toStr()})')
            return TriviaContentCode.ILLEGAL_TRIVIA_TYPE

        if await self.__bannedTriviaIdsRepository.isBanned(
            triviaId = question.getTriviaId(),
            triviaSource = question.getTriviaSource()
        ):
            return TriviaContentCode.IS_BANNED

        contentScannerCode = await self.__triviaContentScanner.verify(question)
        if contentScannerCode is not TriviaContentCode.OK:
            return contentScannerCode

        historyRepositoryCode = await self.__triviaHistoryRepository.verify(
            question = question, 
            emote = emote,
            twitchChannel = triviaFetchOptions.getTwitchChannel()
        )

        if historyRepositoryCode is not TriviaContentCode.OK:
            return historyRepositoryCode

        return TriviaContentCode.OK
