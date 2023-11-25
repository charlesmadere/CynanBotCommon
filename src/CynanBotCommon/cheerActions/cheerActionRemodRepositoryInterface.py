from abc import ABC, abstractmethod
from typing import List

try:
    from CynanBotCommon.cheerActions.cheerActionRemodData import \
        CheerActionRemodData
except:
    from cheerActions.cheerActionRemodData import CheerActionRemodData


class CheerActionRemodRepositoryInterface(ABC):

    @abstractmethod
    async def add(self, data: CheerActionRemodData):
        pass

    @abstractmethod
    async def delete(self, broadcasterUserId: str, userId: str):
        pass

    @abstractmethod
    async def getAll(self) -> List[CheerActionRemodData]:
        pass
