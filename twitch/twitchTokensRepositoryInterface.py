from abc import ABC, abstractmethod
from typing import List, Optional

try:
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
    from CynanBotCommon.twitch.twitchTokensRepositoryListener import \
        TwitchTokensRepositoryListener
except:
    from twitch.twitchTokensDetails import TwitchTokensDetails
    from twitch.twitchTokensRepositoryListener import \
        TwitchTokensRepositoryListener


class TwitchTokensRepositoryInterface(ABC):

    @abstractmethod
    async def addUser(self, code: str, twitchChannel: str):
        pass

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    async def getAccessToken(self, twitchChannel: str) -> Optional[str]:
        pass

    @abstractmethod
    async def getExpiringTwitchChannels(self) -> Optional[List[str]]:
        pass

    @abstractmethod
    async def getRefreshToken(self, twitchChannel: str) -> Optional[str]:
        pass

    @abstractmethod
    async def hasAccessToken(self, twitchChannel: str) -> bool:
        pass

    @abstractmethod
    async def removeUser(self, twitchChannel: str):
        pass

    @abstractmethod
    async def requireAccessToken(self, twitchChannel: str) -> str:
        pass

    @abstractmethod
    async def requireRefreshToken(self, twitchChannel: str) -> str:
        pass

    @abstractmethod
    async def requireTokensDetails(self, twitchChannel: str) -> TwitchTokensDetails:
        pass

    @abstractmethod
    def setListener(self, listener: Optional[TwitchTokensRepositoryListener]):
        pass

    @abstractmethod
    async def validateAndRefreshAccessToken(self, twitchChannel: str):
        pass
