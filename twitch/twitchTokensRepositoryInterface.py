from typing import List, Optional

try:
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
    from CynanBotCommon.twitch.twitchTokensRepositoryListener import \
        TwitchTokensRepositoryListener
except:
    from twitch.twitchTokensDetails import TwitchTokensDetails
    from twitch.twitchTokensRepositoryListener import \
        TwitchTokensRepositoryListener


class TwitchTokensRepositoryInterface():

    async def addUser(self, code: str, twitchChannel: str):
        pass

    async def clearCaches(self):
        pass

    async def getAccessToken(self, twitchChannel: str) -> Optional[str]:
        pass

    async def getExpiringTwitchChannels(self) -> Optional[List[str]]:
        pass

    async def getRefreshToken(self, twitchChannel: str) -> Optional[str]:
        pass

    async def hasAccessToken(self, twitchChannel: str) -> bool:
        pass

    async def removeUser(self, twitchChannel: str):
        pass

    async def requireAccessToken(self, twitchChannel: str) -> str:
        pass

    async def requireRefreshToken(self, twitchChannel: str) -> str:
        pass

    async def requireTokensDetails(self, twitchChannel: str) -> TwitchTokensDetails:
        pass

    def setListener(self, listener: Optional[TwitchTokensRepositoryListener]):
        pass

    async def validateAndRefreshAccessToken(self, twitchChannel: str):
        pass
