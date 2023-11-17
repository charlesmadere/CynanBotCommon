from abc import ABC, abstractmethod

try:
    from CynanBotCommon.users.userInterface import UserInterface
except:
    from users.userInterface import UserInterface


class CheerActionHelperInterface(ABC):

    @abstractmethod
    def getDefaultTimeoutDurationSeconds(self) -> int:
        pass

    @abstractmethod
    async def handleCheerAction(
        self,
        bits: int,
        cheerUserId: str,
        message: str,
        user: UserInterface
    ):
        pass
