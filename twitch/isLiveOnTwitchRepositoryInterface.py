from abc import abstractmethod
from typing import Dict, List


class IsLiveOnTwitchRepositoryInterface():

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    async def isLive(self, twitchHandles: List[str]) -> Dict[str, bool]:
        pass
