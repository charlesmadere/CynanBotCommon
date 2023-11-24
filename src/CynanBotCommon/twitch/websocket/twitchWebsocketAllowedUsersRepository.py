from typing import Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketAllowedUsersRepositoryInterface import \
        TwitchWebsocketAllowedUsersRepositoryInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketUser import \
        TwitchWebsocketUser
    from CynanBotCommon.users.userIdsRepositoryInterface import \
        UserIdsRepositoryInterface
    from CynanBotCommon.users.usersRepositoryInterface import \
        UsersRepositoryInterface
except:
    import utils
    from timber.timberInterface import TimberInterface

    from twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from twitch.websocket.twitchWebsocketAllowedUsersRepositoryInterface import \
        TwitchWebsocketAllowedUsersRepositoryInterface
    from twitch.websocket.twitchWebsocketUser import TwitchWebsocketUser
    from users.userIdsRepositoryInterface import UserIdsRepositoryInterface
    from users.usersRepositoryInterface import UsersRepositoryInterface


class TwitchWebsocketAllowedUsersRepository(TwitchWebsocketAllowedUsersRepositoryInterface):

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

    async def __buildTwitchWebsocketUsers(
        self,
        usersWithTwitchTokens: Set[str]
    ) -> Set[TwitchWebsocketUser]:
        users: Set[TwitchWebsocketUser] = set()

        if not utils.hasItems(usersWithTwitchTokens):
            return users

        for user in usersWithTwitchTokens:
            twitchAccessToken = await self.__validateAndRefreshAccessToken(user)

            if not utils.isValidStr(twitchAccessToken):
                self.__timber.log('TwitchWebsocketAllowedUsersRepository', f'Unable to find Twitch access token for \"{user}\"')
                continue

            userId = await self.__userIdsRepository.fetchUserId(
                userName = user,
                twitchAccessToken = twitchAccessToken
            )

            if not utils.isValidStr(userId):
                self.__timber.log('TwitchWebsocketAllowedUsersRepository', f'Unable to find user ID for \"{user}\" using Twitch access token \"{twitchAccessToken}\"')
                continue

            users.add(TwitchWebsocketUser(
                userId = userId,
                userName = user
            ))

        return users

    async def __findUsersWithTwitchTokens(self, enabledUsers: Set[str]) -> Set[str]:
        usersWithTwitchTokens: Set[str] = set()

        if not utils.hasItems(enabledUsers):
            return usersWithTwitchTokens

        for user in enabledUsers:
            if await self.__twitchTokensRepository.hasAccessToken(user):
                usersWithTwitchTokens.add(user)

        return usersWithTwitchTokens

    async def __getEnabledUsers(self) -> Set[str]:
        enabledUsers: Set[str] = set()
        users = await self.__usersRepository.getUsersAsync()

        for user in users:
            if user.isEnabled():
                enabledUsers.add(user.getHandle())

        return enabledUsers

    async def getUsers(self) -> Set[TwitchWebsocketUser]:
        enabledUsers = await self.__getEnabledUsers()
        usersWithTwitchTokens = await self.__findUsersWithTwitchTokens(enabledUsers)
        users = await self.__buildTwitchWebsocketUsers(usersWithTwitchTokens)

        self.__timber.log('TwitchWebsocketAllowedUsersRepository', f'Built up a list of {len(users)} user(s) that are eligible for websocket connections')

        return users
 
    async def __validateAndRefreshAccessToken(self, user: str) -> Optional[str]:
        if not utils.isValidStr(user):
            raise ValueError(f'user argument is malformed: \"{user}\"')
 
        await self.__twitchTokensRepository.validateAndRefreshAccessToken(user)
        return await self.__twitchTokensRepository.getAccessToken(user)
 