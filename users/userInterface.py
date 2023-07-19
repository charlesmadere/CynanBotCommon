from abc import ABC, abstractmethod


class UserInterface(ABC):

    @abstractmethod
    def areRecurringActionsEnabled(self) -> bool:
        pass

    @abstractmethod
    def getHandle(self) -> str:
        pass

    @abstractmethod
    def isEnabled(self) -> bool:
        pass
