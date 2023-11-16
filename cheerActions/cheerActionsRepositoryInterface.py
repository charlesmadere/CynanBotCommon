from abc import ABC, abstractmethod
from typing import List

try:
    from CynanBotCommon.cheerActions.cheerAction import CheerAction
except:
    from cheerActions.cheerAction import CheerAction


class CheerActionsRepositoryInterface(ABC):

    @abstractmethod
    async def getActions(self, userId: str) -> List[CheerAction]:
        pass
