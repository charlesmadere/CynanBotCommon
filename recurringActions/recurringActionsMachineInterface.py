from abc import abstractmethod
from typing import Optional

try:
    from CynanBotCommon.recurringActions.recurringActionEventListener import \
        RecurringActionEventListener
except:
    from recurringActions.recurringActionEventListener import \
        RecurringActionEventListener


class RecurringActionsMachineInterface():

    def __init__(self):
        pass

    @abstractmethod
    def setRecurringActionListener(self, listener: Optional[RecurringActionEventListener]):
        pass

    @abstractmethod
    def startRecurringActions(self):
        pass
