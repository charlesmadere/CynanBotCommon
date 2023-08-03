from abc import ABC, abstractmethod

try:
    from CynanBotCommon.recurringActions.recurringEventType import \
        RecurringEventType
except:
    from recurringActions.recurringEventType import RecurringEventType


class RecurringEvent(ABC):

    @abstractmethod
    def getEventType(self) -> RecurringEventType:
        pass
