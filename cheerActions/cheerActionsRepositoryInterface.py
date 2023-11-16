from abc import ABC, abstractmethod
from typing import List, Optional

try:
    from CynanBotCommon.cheerActions.cheerAction import CheerAction
except:
    from cheerActions.cheerAction import CheerAction


class CheerActionsRepositoryInterface(ABC):

    @abstractmethod
    async def addAction(self, action: CheerAction):
        pass

    @abstractmethod
    async def deleteAction(self, actionId: str) -> Optional[CheerAction]:
        pass

    @abstractmethod
    async def getAction(self, actionId: str) -> Optional[CheerAction]:
        pass

    @abstractmethod
    async def getActions(self, userId: str) -> List[CheerAction]:
        pass
