import re
import traceback
from typing import List, Optional, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.administratorProviderInterface import \
        AdministratorProviderInterface
    from CynanBotCommon.cheerActions.cheerAction import CheerAction
    from CynanBotCommon.cheerActions.cheerActionHelperInterface import \
        CheerActionHelperInterface
    from CynanBotCommon.cheerActions.cheerActionRequirement import \
        CheerActionRequirement
    from CynanBotCommon.cheerActions.cheerActionsRepositoryInterface import \
        CheerActionsRepositoryInterface
    from CynanBotCommon.cheerActions.cheerActionType import CheerActionType
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.twitchApiServiceInterface import \
        TwitchApiServiceInterface
    from CynanBotCommon.twitch.twitchBanRequest import TwitchBanRequest
    from CynanBotCommon.twitch.twitchBanResponse import TwitchBanResponse
    from CynanBotCommon.twitch.twitchHandleProviderInterface import \
        TwitchHandleProviderInterface
    from CynanBotCommon.twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from CynanBotCommon.users.userIdsRepositoryInterface import \
        UserIdsRepositoryInterface
    from CynanBotCommon.users.userInterface import UserInterface
except:
    import utils
    from administratorProviderInterface import AdministratorProviderInterface
    from cheerActions.cheerAction import CheerAction
    from cheerActions.cheerActionHelperInterface import \
        CheerActionHelperInterface
    from cheerActions.cheerActionRequirement import CheerActionRequirement
    from cheerActions.cheerActionsRepositoryInterface import \
        CheerActionsRepositoryInterface
    from cheerActions.cheerActionType import CheerActionType
    from timber.timberInterface import TimberInterface

    from twitch.twitchApiServiceInterface import TwitchApiServiceInterface
    from twitch.twitchBanRequest import TwitchBanRequest
    from twitch.twitchBanResponse import TwitchBanResponse
    from twitch.twitchHandleProviderInterface import \
        TwitchHandleProviderInterface
    from twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from users.userIdsRepositoryInterface import UserIdsRepositoryInterface
    from users.userInterface import UserInterface


class CheerActionHelper(CheerActionHelperInterface):

    def __init__(
        self,
        administratorProvider: AdministratorProviderInterface,
        cheerActionsRepository: CheerActionsRepositoryInterface,
        timber: TimberInterface,
        twitchApiService: TwitchApiServiceInterface,
        twitchHandleProvider: TwitchHandleProviderInterface,
        twitchTokensRepository: TwitchTokensRepositoryInterface,
        userIdsRepository: UserIdsRepositoryInterface,
        defaultTimeoutDurationSeconds: int = 60
    ):
        if not isinstance(administratorProvider, AdministratorProviderInterface):
            raise ValueError(f'administratorProvider argument is malformed: \"{administratorProvider}\"')
        elif not isinstance(cheerActionsRepository, CheerActionHelperInterface):
            raise ValueError(f'cheerActionsRepository argument is malformed: \"{cheerActionsRepository}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchApiService, TwitchApiServiceInterface):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')
        elif not isinstance(twitchHandleProvider, TwitchHandleProviderInterface):
            raise ValueError(f'twitchHandleProvider argument is malformed: \"{twitchHandleProvider}\"')
        elif not isinstance(twitchTokensRepository, TwitchTokensRepositoryInterface):
            raise ValueError(f'twitchTokensRepository argument is malformed: \"{twitchTokensRepository}\"')
        elif not isinstance(userIdsRepository, UserIdsRepositoryInterface):
            raise ValueError(f'userIdsRepository argument is malformed: \"{userIdsRepository}\"')
        elif not utils.isValidInt(defaultTimeoutDurationSeconds):
            raise ValueError(f'defaultTimeoutDurationSeconds argument is malformed: \"{defaultTimeoutDurationSeconds}\"')
        elif defaultTimeoutDurationSeconds < 1 or defaultTimeoutDurationSeconds > 1209600:
            raise ValueError(f'defaultTimeoutDurationSeconds argument is out of bounds: {defaultTimeoutDurationSeconds}')

        self.__administratorProvider: AdministratorProviderInterface = administratorProvider
        self.__cheerActionsRepository: CheerActionsRepositoryInterface = cheerActionsRepository
        self.__timber: TimberInterface = timber
        self.__twitchApiService: TwitchApiServiceInterface = twitchApiService
        self.__twitchHandleProvider: TwitchHandleProviderInterface = twitchHandleProvider
        self.__twitchTokensRepository: TwitchTokensRepositoryInterface = twitchTokensRepository
        self.__userIdsRepository: UserIdsRepositoryInterface = userIdsRepository
        self.__defaultTimeoutDurationSeconds: int = defaultTimeoutDurationSeconds

        self.__cheerMessageRegEx: Pattern = re.compile(r'(^|\s+)[a-z]+[0-9]+(\s+|$)', re.IGNORECASE)
        self.__userNameRegEx: Pattern = re.compile(r'^\s*@?(\w+)\s*$', re.IGNORECASE)

    def getDefaultTimeoutDurationSeconds(self) -> int:
        return self.__defaultTimeoutDurationSeconds

    async def __getTwitchAccessToken(self, user: UserInterface) -> Optional[str]:
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')

        if await self.__twitchTokensRepository.hasAccessToken(user.getHandle()):
            await self.__twitchTokensRepository.validateAndRefreshAccessToken(user.getHandle())
            return await self.__twitchTokensRepository.getAccessToken(user.getHandle())
        else:
            administratorUserName = await self.__administratorProvider.getAdministratorUserName()
            await self.__twitchTokensRepository.validateAndRefreshAccessToken(administratorUserName)
            return await self.__twitchTokensRepository.getAccessToken(administratorUserName)

    async def handleCheerAction(
        self,
        bits: int,
        cheerUserId: str,
        message: str,
        user: UserInterface
    ):
        if not utils.isValidInt(bits):
            raise ValueError(f'bits argument is malformed: \"{bits}\"')
        elif bits < 0 or bits > utils.getIntMaxSafeSize():
            raise ValueError(f'bits argument is out of bounds: {bits}')
        elif not utils.isValidStr(cheerUserId):
            raise ValueError(f'cheerUserId argument is malformed: \"{cheerUserId}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')
        elif not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')

        twitchAccessToken = await self.__getTwitchAccessToken(user)

        broadcasterUserId = await self.__userIdsRepository.requireUserId(
            userName = user.getHandle(),
            twitchAccessToken = await self.__getTwitchAccessToken(user)
        )

        actions = await self.__cheerActionsRepository.getActions(broadcasterUserId)

        if not utils.isValidStr(twitchAccessToken) or not utils.hasItems(actions):
            return

        await self.__processTimeoutActions(
            bits = bits,
            actions = actions,
            broadcasterUserId = broadcasterUserId,
            cheerUserId = cheerUserId,
            message = message,
            twitchAccessToken = twitchAccessToken,
            user = user
        )

    async def __processTimeoutActions(
        self,
        bits: int,
        actions: List[CheerAction],
        broadcasterUserId: str,
        cheerUserId: str,
        message: str,
        twitchAccessToken: str,
        user: UserInterface
    ):
        if not utils.isValidInt(bits):
            raise ValueError(f'bits argument is malformed: \"{bits}\"')
        elif bits < 0 or bits > utils.getIntMaxSafeSize():
            raise ValueError(f'bits argument is out of bounds: {bits}')
        elif not isinstance(actions, List):
            raise ValueError(f'actions argument is malformed: \"{actions}\"')
        elif not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        elif not utils.isValidStr(cheerUserId):
            raise ValueError(f'cheerUserId argument is malformed: \"{cheerUserId}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')
        elif not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')

        timeoutActions: List[CheerAction] = list()

        for action in actions:
            if action.getActionType() is CheerActionType.TIMEOUT:
                timeoutActions.append(action)

        if len(timeoutActions) == 0:
            return

        messageWithCheerRemoved = self.__cheerMessageRegEx.sub('', message)
        if not utils.isValidStr(messageWithCheerRemoved):
            return

        userNameToTimeoutMatch = self.__userNameRegEx.fullmatch(message)
        if userNameToTimeoutMatch is None or not utils.isValidStr(userNameToTimeoutMatch.group(1)):
            return

        userNameToTimeout = userNameToTimeoutMatch.group(1)

        moderatorUserId = await self.__userIdsRepository.requireUserId(
            userName = await self.__twitchHandleProvider.getTwitchHandle(),
            twitchAccessToken = twitchAccessToken
        )

        userIdToTimeout = await self.__userIdsRepository.fetchUserId(
            userName = userNameToTimeout,
            twitchAccessToken = twitchAccessToken
        )

        if not utils.isValidStr(userIdToTimeout):
            self.__timber.log('CheerActionHelper', f'Unable to find user ID for \"{userNameToTimeout}\" ({message=})')
            return
        elif userIdToTimeout.lower() == broadcasterUserId.lower():
            userIdToTimeout = cheerUserId
            self.__timber.log('CheerActionHelper', f'Attempted to timeout the broadcaster themself ({userIdToTimeout=}) ({broadcasterUserId=}) ({message=}), so will instead time out the user')
            return

        for action in timeoutActions:
            if action.getActionRequirement() is CheerActionRequirement.EXACT and action.getAmount() == bits:
                await self.__timeoutUser(
                    action = action,
                    broadcasterUserId = broadcasterUserId,
                    moderatorUserId = moderatorUserId,
                    userIdToTimeout = userIdToTimeout,
                    user = user
                )

                return

        greaterThanOrEqualToActions: List[CheerAction] = list()

        for action in timeoutActions:
            if action.getActionRequirement() is CheerActionRequirement.GREATER_THAN_OR_EQUAL_TO:
                greaterThanOrEqualToActions.append(action)

        greaterThanOrEqualToActions.sort(key = lambda action: action.getAmount(), reverse = True)

        for action in greaterThanOrEqualToActions:
            if bits >= action.getAmount():
                await self.__timeoutUser(
                    action = action,
                    broadcasterUserId = broadcasterUserId,
                    moderatorUserId = moderatorUserId,
                    twitchAccessToken = twitchAccessToken,
                    userIdToTimeout = userIdToTimeout,
                    user = user
                )

                return

        self.__timber.log('CheerActionHelper', f'Unable to find a matching timeout cheer value in \"{user.getHandle()}\" ({userIdToTimeout=}) ({broadcasterUserId=}) ({moderatorUserId=}) ({message=}) ({bits=}) ({timeoutActions=}) ({greaterThanOrEqualToActions=})')

    async def __timeoutUser(
        self,
        action: CheerAction,
        broadcasterUserId: str,
        moderatorUserId: str,
        twitchAccessToken: str,
        userIdToTimeout: str,
        user: UserInterface
    ):
        if not isinstance(action, CheerAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        elif not utils.isValidStr(moderatorUserId):
            raise ValueError(f'moderatorUserId argument is malformed: \"{moderatorUserId}\"')
        elif not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not utils.isValidStr(userIdToTimeout):
            raise ValueError(f'userIdToTimeout argument is malformed: \"{userIdToTimeout}\"')
        elif not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')

        timeoutDurationSeconds = action.getDurationSeconds()

        if timeoutDurationSeconds is None:
            timeoutDurationSeconds = self.__defaultTimeoutDurationSeconds

        banRequest = TwitchBanRequest(
            duration = timeoutDurationSeconds,
            broadcasterUserId = broadcasterUserId,
            moderatorUserId = moderatorUserId,
            reason = None,
            userIdToBan = userIdToTimeout
        )

        response: Optional[TwitchBanResponse] = None
        exception: Optional[Exception] = None

        try:
            response = await self.__twitchApiService.banUser(
                twitchAccessToken = twitchAccessToken,
                banRequest = banRequest
            )
        except Exception as e:
            exception = e

        if exception is not None or response is None:
            self.__timber.log('CheerActionHelper', f'Failed to timeout {userIdToTimeout=} in \"{user.getHandle()}\": {exception}', exception, traceback.format_exc())
        else:
            self.__timber.log('CheerActionHelper', f'Timed out {userIdToTimeout=} in \"{user.getHandle()}\": {response}')
