from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

try:
    from CynanBotCommon.twitch.twitchBanRequest import TwitchBanRequest
    from CynanBotCommon.twitch.twitchBanResponse import TwitchBanResponse
    from CynanBotCommon.twitch.twitchEmoteDetails import TwitchEmoteDetails
    from CynanBotCommon.twitch.twitchEventSubRequest import \
        TwitchEventSubRequest
    from CynanBotCommon.twitch.twitchEventSubResponse import \
        TwitchEventSubResponse
    from CynanBotCommon.twitch.twitchLiveUserDetails import \
        TwitchLiveUserDetails
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
    from CynanBotCommon.twitch.twitchUnbanRequest import TwitchUnbanRequest
    from CynanBotCommon.twitch.twitchUserDetails import TwitchUserDetails
    from CynanBotCommon.twitch.twitchUserSubscriptionDetails import \
        TwitchUserSubscriptionDetails
except:
    from twitch.twitchBanRequest import TwitchBanRequest
    from twitch.twitchBanResponse import TwitchBanResponse
    from twitch.twitchEmoteDetails import TwitchEmoteDetails
    from twitch.twitchEventSubRequest import TwitchEventSubRequest
    from twitch.twitchEventSubResponse import TwitchEventSubResponse
    from twitch.twitchLiveUserDetails import TwitchLiveUserDetails
    from twitch.twitchTokensDetails import TwitchTokensDetails
    from twitch.twitchUnbanRequest import TwitchUnbanRequest
    from twitch.twitchUserDetails import TwitchUserDetails
    from twitch.twitchUserSubscriptionDetails import \
        TwitchUserSubscriptionDetails


class TwitchApiServiceInterface(ABC):

    @abstractmethod
    async def banUser(
        self,
        twitchAccessToken: str,
        banRequest: TwitchBanRequest
    ) -> TwitchBanResponse:
        pass

    @abstractmethod
    async def createEventSubSubscription(
        self,
        twitchAccessToken: str,
        eventSubRequest: TwitchEventSubRequest
    ) -> TwitchEventSubResponse:
        pass

    @abstractmethod
    async def fetchEmoteDetails(
        self,
        broadcasterId: str,
        twitchAccessToken: str
    ) -> List[TwitchEmoteDetails]:
        pass

    @abstractmethod
    async def fetchLiveUserDetails(
        self,
        twitchAccessToken: str,
        userNames: List[str]
    ) -> List[TwitchLiveUserDetails]:
        pass

    @abstractmethod
    async def fetchTokens(self, code: str) -> TwitchTokensDetails:
        pass

    @abstractmethod
    async def fetchUserDetails(
        self,
        twitchAccessToken: str,
        userName: str
    ) -> Optional[TwitchUserDetails]:
        pass

    @abstractmethod
    async def fetchUserSubscriptionDetails(
        self,
        broadcasterId: str,
        twitchAccessToken: str,
        userId: str
    ) -> Optional[TwitchUserSubscriptionDetails]:
        pass

    @abstractmethod
    async def refreshTokens(self, twitchRefreshToken: str) -> TwitchTokensDetails:
        pass

    @abstractmethod
    async def unbanUser(
        self,
        twitchAccessToken: str,
        unbanRequest: TwitchUnbanRequest
    ) -> bool:
        pass

    @abstractmethod
    async def validateTokens(self, twitchAccessToken: str) -> Optional[datetime]:
        pass
