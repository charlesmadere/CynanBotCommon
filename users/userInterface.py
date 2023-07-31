from abc import ABC, abstractmethod
from typing import Optional


class UserInterface(ABC):

    @abstractmethod
    def areRecurringActionsEnabled(self) -> bool:
        pass

    @abstractmethod
    def getHandle(self) -> str:
        pass

    @abstractmethod
    def getLocationId(self) -> Optional[str]:
        pass

    @abstractmethod
    def getSuperTriviaGamePoints(self) -> Optional[int]:
        pass

    @abstractmethod
    def getSuperTriviaGameShinyMultiplier(self) -> Optional[int]:
        pass

    @abstractmethod
    def getSuperTriviaGameToxicMultiplier(self) -> Optional[int]:
        pass

    @abstractmethod
    def getSuperTriviaGameToxicPunishmentMultiplier(self) -> Optional[int]:
        pass

    @abstractmethod
    def getSuperTriviaPerUserAttempts(self) -> Optional[int]:
        pass

    @abstractmethod
    def getTriviaGamePoints(self) -> Optional[int]:
        pass

    @abstractmethod
    def getTriviaGameShinyMultiplier(self) -> Optional[int]:
        pass

    @abstractmethod
    def getWaitForSuperTriviaAnswerDelay(self) -> Optional[int]:
        pass

    @abstractmethod
    def getWaitForTriviaAnswerDelay(self) -> Optional[int]:
        pass

    @abstractmethod
    def hasLocationId(self) -> bool:
        pass

    @abstractmethod
    def hasSuperTriviaGamePoints(self) -> bool:
        pass

    @abstractmethod
    def hasSuperTriviaPerUserAttempts(self) -> bool:
        pass

    @abstractmethod
    def hasSuperTriviaGameShinyMultiplier(self) -> bool:
        pass

    @abstractmethod
    def hasSuperTriviaGameToxicMultiplier(self) -> bool:
        pass

    @abstractmethod
    def hasSuperTriviaGameToxicPunishmentMultiplier(self) -> bool:
        pass

    @abstractmethod
    def hasTriviaGamePoints(self) -> bool:
        pass

    @abstractmethod
    def hasTriviaGameShinyMultiplier(self) -> bool:
        pass

    @abstractmethod
    def hasWaitForSuperTriviaAnswerDelay(self) -> bool:
        pass

    @abstractmethod
    def hasWaitForTriviaAnswerDelay(self) -> bool:
        pass

    @abstractmethod
    def isEnabled(self) -> bool:
        pass

    @abstractmethod
    def isJokeTriviaRepositoryEnabled(self) -> bool:
        pass

    @abstractmethod
    def isShinyTriviaEnabled(self) -> bool:
        pass

    @abstractmethod
    def isSuperTriviaGameEnabled(self) -> bool:
        pass

    @abstractmethod
    def isToxicTriviaEnabled(self) -> bool:
        pass

    @abstractmethod
    def isTriviaGameEnabled(self) -> bool:
        pass
