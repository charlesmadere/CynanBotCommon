from abc import ABC, abstractmethod

try:
    from CynanBotCommon.recurringActions.recurringEvent import RecurringEvent
except:
    from recurringActions.recurringEvent import RecurringEvent


class RecurringActionEventListener(ABC):

    @abstractmethod
    async def onNewRecurringActionEvent(self, event: RecurringEvent):
        pass
