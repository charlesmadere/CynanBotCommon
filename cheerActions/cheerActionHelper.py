try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cheerActions.cheerActionHelperInterface import \
        CheerActionHelperInterface
    from CynanBotCommon.cheerActions.cheerActionsRepositoryInterface import \
        CheerActionsRepositoryInterface
    from CynanBotCommon.twitch.twitchApiServiceInterface import \
        TwitchApiServiceInterface
    from CynanBotCommon.users.userInterface import UserInterface
except:
    import utils
    from cheerActions.cheerActionHelperInterface import \
        CheerActionHelperInterface
    from cheerActions.cheerActionsRepositoryInterface import \
        CheerActionsRepositoryInterface

    from twitch.twitchApiServiceInterface import TwitchApiServiceInterface
    from users.userInterface import UserInterface


class CheerActionHelper(CheerActionHelperInterface):

    def __init__(
        self,
        cheerActionsRepository: CheerActionsRepositoryInterface,
        twitchApiService: TwitchApiServiceInterface
    ):
        if not isinstance(cheerActionsRepository, CheerActionHelperInterface):
            raise ValueError(f'cheerActionsRepository argument is malformed: \"{cheerActionsRepository}\"')
        elif not isinstance(twitchApiService, TwitchApiServiceInterface):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')

        self.__cheerActionsRepository: CheerActionsRepositoryInterface = cheerActionsRepository
        self.__twitchApiService: TwitchApiServiceInterface = twitchApiService

    async def handleCheerAction(
        self,
        bits: int,
        message: str,
        user: UserInterface
    ):
        if not utils.isValidInt(bits):
            raise ValueError(f'bits argument is malformed: \"{bits}\"')
        elif bits < 0 or bits > utils.getIntMaxSafeSize():
            raise ValueError(f'bits argument is out of bounds: {bits}')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')
        elif not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')

        pass
