from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

try:
    from CynanBotCommon.twitch.twitchEmoteDetails import TwitchEmoteDetails
    from CynanBotCommon.twitch.twitchLiveUserDetails import \
        TwitchLiveUserDetails
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
    from CynanBotCommon.twitch.twitchUserDetails import TwitchUserDetails
    from CynanBotCommon.twitch.twitchUserSubscriptionDetails import \
        TwitchUserSubscriptionDetails
except:
    from twitch.twitchEmoteDetails import TwitchEmoteDetails
    from twitch.twitchLiveUserDetails import TwitchLiveUserDetails
    from twitch.twitchTokensDetails import TwitchTokensDetails
    from twitch.twitchUserDetails import TwitchUserDetails
    from twitch.twitchUserSubscriptionDetails import \
        TwitchUserSubscriptionDetails


class TwitchApiServiceInterface(ABC):

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
    async def validateTokens(self, twitchAccessToken: str) -> Optional[datetime]:
        pass
