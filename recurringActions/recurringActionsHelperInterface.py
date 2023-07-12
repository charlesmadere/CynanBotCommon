from abc import abstractmethod
from typing import Optional

try:
    from CynanBotCommon.recurringActions.recurringActionListener import \
        RecurringActionListener
except:
    from recurringActions.recurringActionListener import \
        RecurringActionListener


class RecurringActionsHelperInterface():

    def __init__(self):
        pass

    @abstractmethod
    def setRecurringActionListener(self, listener: Optional[RecurringActionListener]):
        pass

    @abstractmethod
    def startRecurringActions(self):
        pass
