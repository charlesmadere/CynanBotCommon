from abc import abstractmethod
from typing import List, Optional

try:
    from CynanBotCommon.cheerActions.cheerAction import CheerAction
    from CynanBotCommon.clearable import Clearable
except:
    from cheerActions.cheerAction import CheerAction
    from clearable import Clearable


class CheerActionsRepositoryInterface(Clearable):

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
