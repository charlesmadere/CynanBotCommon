from datetime import timedelta
from typing import Dict, List, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.administratorProviderInterface import \
        AdministratorProviderInterface
    from CynanBotCommon.timedDict import TimedDict
    from CynanBotCommon.twitch.isLiveOnTwitchRepositoryInterface import \
        IsLiveOnTwitchRepositoryInterface
    from CynanBotCommon.twitch.twitchApiServiceInterface import \
        TwitchApiServiceInterface
    from CynanBotCommon.twitch.twitchStreamType import TwitchStreamType
    from CynanBotCommon.twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
except:
    import utils
    from administratorProviderInterface import AdministratorProviderInterface
    from timedDict import TimedDict

    from twitch.isLiveOnTwitchRepositoryInterface import \
        IsLiveOnTwitchRepositoryInterface
    from twitch.twitchApiServiceInterface import TwitchApiServiceInterface
    from twitch.twitchStreamType import TwitchStreamType
    from twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface


class IsLiveOnTwitchRepository(IsLiveOnTwitchRepositoryInterface):

    def __init__(
        self,
        administratorProvider: AdministratorProviderInterface,
        twitchApiService: TwitchApiServiceInterface,
        twitchTokensRepository: TwitchTokensRepositoryInterface,
        cacheTimeDelta: timedelta = timedelta(minutes = 10)
    ):
        if not isinstance(administratorProvider, AdministratorProviderInterface):
            raise ValueError(f'administratorProvider argument is malformed: \"{administratorProvider}\"')
        elif not isinstance(twitchApiService, TwitchApiServiceInterface):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')
        elif not isinstance(twitchTokensRepository, TwitchTokensRepositoryInterface):
            raise ValueError(f'twitchTokensRepositoryInterface argument is malformed: \"{twitchTokensRepository}\"')
        elif not isinstance(cacheTimeDelta, timedelta):
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__administratorProvider: AdministratorProviderInterface = administratorProvider
        self.__twitchApiService: TwitchApiServiceInterface = twitchApiService
        self.__twitchTokensRepository: TwitchTokensRepositoryInterface = twitchTokensRepository

        self.__cache: TimedDict = TimedDict(cacheTimeDelta)

    async def clearCaches(self):
        self.__cache.clear()

    async def __fetchLiveUserDetails(
        self,
        twitchHandles: List[str],
        twitchHandlesToLiveStatus: Dict[str, bool]
    ):
        twitchHandlesToFetch: Set[str] = set()

        for twitchHandle in twitchHandles:
            if twitchHandle.lower() in twitchHandlesToLiveStatus:
                continue

            twitchHandlesToFetch.add(twitchHandle.lower())

        if not utils.hasItems(twitchHandlesToFetch):
            return

        userName = await self.__administratorProvider.getAdministratorUserName()

        await self.__twitchTokensRepository.validateAndRefreshAccessToken(userName)
        twitchAccessToken = await self.__twitchTokensRepository.requireAccessToken(userName)

        liveUserDetails = await self.__twitchApiService.fetchLiveUserDetails(
            twitchAccessToken = twitchAccessToken,
            userNames = list(twitchHandlesToFetch)
        )

        for liveUserDetail in liveUserDetails:
            isLive = liveUserDetail.getStreamType() is TwitchStreamType.LIVE
            twitchHandlesToLiveStatus[liveUserDetail.getUserName().lower()] = isLive
            self.__cache[liveUserDetail.getUserName().lower()] = isLive

        for twitchHandle in twitchHandles:
            if twitchHandle.lower() not in twitchHandlesToLiveStatus:
                twitchHandlesToLiveStatus[twitchHandle.lower()] = False
                self.__cache[twitchHandle.lower()] = False

    async def isLive(self, twitchHandles: List[str]) -> Dict[str, bool]:
        twitchHandlesToLiveStatus: Dict[str, bool] = dict()

        if not utils.hasItems(twitchHandles):
            return twitchHandlesToLiveStatus

        await self.__populateFromCache(
            twitchHandles = twitchHandles,
            twitchHandlesToLiveStatus = twitchHandlesToLiveStatus
        )

        await self.__fetchLiveUserDetails(
            twitchHandles = twitchHandles,
            twitchHandlesToLiveStatus = twitchHandlesToLiveStatus
        )

        return twitchHandlesToLiveStatus

    async def __populateFromCache(
        self,
        twitchHandles: List[str],
        twitchHandlesToLiveStatus: Dict[str, bool]
    ):
        for twitchHandle in twitchHandles:
            isLive = self.__cache[twitchHandle.lower()]

            if utils.isValidBool(isLive):
                twitchHandlesToLiveStatus[twitchHandle.lower()] = isLive
