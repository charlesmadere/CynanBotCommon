try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.funtoon.funtoonRepository import FuntoonRepository
    from CynanBotCommon.trivia.bannedTriviaIdsRepository import \
        BannedTriviaIdsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from funtoon.funtoonRepository import FuntoonRepository
    from trivia.bannedTriviaIdsRepository import BannedTriviaIdsRepository
    from trivia.triviaSource import TriviaSource


class TriviaBanHelper():

    def __init__(
        self,
        bannedTriviaIdsRepository: BannedTriviaIdsRepository,
        funtoonRepository: FuntoonRepository
    ):
        if not isinstance(bannedTriviaIdsRepository, BannedTriviaIdsRepository):
            raise ValueError(f'bannedTriviaIdsRepository argument is malformed: \"{bannedTriviaIdsRepository}\"')
        elif not isinstance(funtoonRepository, FuntoonRepository):
            raise ValueError(f'funtoonRepository argument is malformed: \"{funtoonRepository}\"')

        self.__bannedTriviaIdsRepository: BannedTriviaIdsRepository = bannedTriviaIdsRepository
        self.__funtoonRepository: FuntoonRepository = funtoonRepository

    async def ban(self, triviaId: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if triviaSource is TriviaSource.FUNTOON:
            await self.__funtoonRepository.banTriviaQuestion(triviaId)
        else:
            await self.__bannedTriviaIdsRepository.ban(triviaId, triviaSource)

    async def unban(self, triviaId: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        return await self.__bannedTriviaIdsRepository.unban(triviaId, triviaSource)
