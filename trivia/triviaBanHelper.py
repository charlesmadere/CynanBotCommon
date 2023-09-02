try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.funtoon.funtoonRepository import FuntoonRepository
    from CynanBotCommon.trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from funtoon.funtoonRepository import FuntoonRepository
    from trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from trivia.triviaSource import TriviaSource


class TriviaBanHelper():

    def __init__(
        self,
        bannedTriviaIdsRepository: BannedTriviaIdsRepositoryInterface,
        funtoonRepository: FuntoonRepository
    ):
        if not isinstance(bannedTriviaIdsRepository, BannedTriviaIdsRepositoryInterface):
            raise ValueError(f'bannedTriviaIdsRepository argument is malformed: \"{bannedTriviaIdsRepository}\"')
        elif not isinstance(funtoonRepository, FuntoonRepository):
            raise ValueError(f'funtoonRepository argument is malformed: \"{funtoonRepository}\"')

        self.__bannedTriviaIdsRepository: BannedTriviaIdsRepositoryInterface = bannedTriviaIdsRepository
        self.__funtoonRepository: FuntoonRepository = funtoonRepository

    async def ban(self, triviaId: str, userId: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if triviaSource is TriviaSource.FUNTOON:
            await self.__funtoonRepository.banTriviaQuestion(triviaId)
        else:
            await self.__bannedTriviaIdsRepository.ban(triviaId, userId, triviaSource)

    async def unban(self, triviaId: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        return await self.__bannedTriviaIdsRepository.unban(triviaId, triviaSource)
