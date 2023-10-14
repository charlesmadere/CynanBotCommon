from typing import List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketAllowedUserIdsRepositoryInterface import \
        TwitchWebsocketAllowedUserIdsRepositoryInterface
    from CynanBotCommon.users.userIdsRepositoryInterface import \
        UserIdsRepositoryInterface
    from CynanBotCommon.users.userInterface import UserInterface
    from CynanBotCommon.users.usersRepositoryInterface import \
        UsersRepositoryInterface
except:
    import utils
    from timber.timberInterface import TimberInterface

    from twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from twitch.websocket.twitchWebsocketAllowedUserIdsRepositoryInterface import \
        TwitchWebsocketAllowedUserIdsRepositoryInterface
    from users.userIdsRepositoryInterface import UserIdsRepositoryInterface
    from users.userInterface import UserInterface
    from users.usersRepositoryInterface import UsersRepositoryInterface


class TwitchWebsocketAllowedUserIdsRepository(TwitchWebsocketAllowedUserIdsRepositoryInterface):

    def __init__(
        self,
        timber: TimberInterface,
        twitchTokensRepository: TwitchTokensRepositoryInterface,
        userIdsRepository: UserIdsRepositoryInterface,
        usersRepository: UsersRepositoryInterface
    ):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchTokensRepository, TwitchTokensRepositoryInterface):
            raise ValueError(f'twitchTokensRepository argument is malformed: \"{twitchTokensRepository}\"')
        elif not isinstance(userIdsRepository, UserIdsRepositoryInterface):
            raise ValueError(f'userIdsRepository argument is malformed: \"{userIdsRepository}\"')
        elif not isinstance(usersRepository, UsersRepositoryInterface):
            raise ValueError(f'usersRepository argument is malformed: \"{usersRepository}\"')

        self.__timber: TimberInterface = timber
        self.__twitchTokensRepository: TwitchTokensRepositoryInterface = twitchTokensRepository
        self.__userIdsRepository: UserIdsRepositoryInterface = userIdsRepository
        self.__usersRepository: UsersRepositoryInterface = usersRepository

        self.__cache: Optional[Set[str]] = None

    async def clearCaches(self):
        self.__cache = None
        self.__timber.log('TwitchWebsocketAllowedUserIdsRepository', 'Caches cleared')

    async def __fetchUserIds(
        self,
        usersWithTwitchTokens: List[UserInterface]
    ) -> Set[str]:
        userIds: Set[str] = set()

        if not utils.hasItems(usersWithTwitchTokens):
            return userIds

        for user in usersWithTwitchTokens:
            userId = await self.__userIdsRepository.fetchUserId(
                userName = user.getHandle(),
                twitchAccessToken = await self.__twitchTokensRepository.getAccessToken(user.getHandle())
            )

            if utils.isValidStr(userId):
                userIds.add(userId)

        return userIds

    async def __findUsersWithTwitchTokens(
        self,
        enabledUsers: List[UserInterface]
    ) -> List[UserInterface]:
        usersWithTwitchTokens: List[UserInterface] = list()

        if not utils.hasItems(enabledUsers):
            return usersWithTwitchTokens

        for user in enabledUsers:
            if await self.__twitchTokensRepository.hasAccessToken(user.getHandle()):
                usersWithTwitchTokens.append(user)

        return usersWithTwitchTokens

    async def __getEnabledUsers(self) -> List[UserInterface]:
        enabledUsers: List[UserInterface] = list()
        users = await self.__usersRepository.getUsersAsync()

        for user in users:
            if user.isEnabled():
                enabledUsers.append(user)

        return enabledUsers

    async def getUserIds(self) -> Set[str]:
        if self.__cache is not None:
            return self.__cache

        enabledUsers = await self.__getEnabledUsers()
        usersWithTwitchTokens = await self.__findUsersWithTwitchTokens(enabledUsers)
        userIds = await self.__fetchUserIds(usersWithTwitchTokens)
        self.__cache = userIds

        self.__timber.log('TwitchWebsocketAllowedUserIdsRepository', f'Built up a list of {len(userIds)} user(s) that are eligible for websocket connections')
        return userIds
