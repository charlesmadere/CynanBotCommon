from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.recurringActions.mostRecentRecurringAction import \
        MostRecentRecurringAction
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
except:
    from recurringActions.mostRecentRecurringAction import \
        MostRecentRecurringAction
    from recurringActions.recurringAction import RecurringAction


class MostRecentRecurringActionRepositoryInterface(ABC):

    @abstractmethod
    async def getMostRecentRecurringAction(
        self,
        twitchChannel: str
    ) -> Optional[MostRecentRecurringAction]:
        pass

    @abstractmethod
    async def setMostRecentRecurringAction(self, action: RecurringAction):
        pass
