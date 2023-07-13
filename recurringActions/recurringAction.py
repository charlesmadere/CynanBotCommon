from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
except:
    from recurringActions.recurringActionType import RecurringActionType


class RecurringAction(ABC):

    @abstractmethod
    def getActionType(self) -> RecurringActionType:
        pass

    @abstractmethod
    def getMinutesBetween(self) -> Optional[int]:
        pass

    @abstractmethod
    def getTwitchChannel(self) -> str:
        pass

    @abstractmethod
    def hasMinutesBetween(self) -> bool:
        pass

    @abstractmethod
    def isEnabled(self) -> bool:
        pass
