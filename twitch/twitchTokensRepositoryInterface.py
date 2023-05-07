from typing import List, Optional


class TwitchTokensRepositoryInterface():

    async def addUser(self, twitchHandle: str, code: str):
        pass

    async def clearCaches(self):
        pass

    async def getAccessToken(self, twitchHandle: str) -> Optional[str]:
        pass

    async def getExpiringTwitchHandles(self) -> Optional[List[str]]:
        pass

    async def getRefreshToken(self, twitchHandle: str) -> Optional[str]:
        pass

    async def hasAccessToken(self, twitchHandle: str) -> bool:
        pass

    async def removeUser(self, twitchHandle: str):
        pass

    async def requireAccessToken(self, twitchHandle: str) -> str:
        pass

    async def requireRefreshToken(self, twitchHandle: str) -> str:
        pass

    async def validateAndRefreshAccessToken(self, twitchHandle: str):
        pass
