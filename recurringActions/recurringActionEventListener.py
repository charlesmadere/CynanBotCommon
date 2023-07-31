from abc import ABC, abstractmethod

try:
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
except:
    from recurringActions.recurringAction import RecurringAction


class RecurringActionEventListener(ABC):

    @abstractmethod
    async def onNewRecurringActionEvent(self, event: RecurringAction):
        pass
