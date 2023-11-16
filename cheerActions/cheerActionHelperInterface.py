from abc import ABC, abstractmethod

try:
    from CynanBotCommon.users.userInterface import UserInterface
except:
    from users.userInterface import UserInterface


class CheerActionHelperInterface(ABC):

    @abstractmethod
    async def handleCheerAction(
        self,
        bits: int,
        message: str,
        user: UserInterface
    ):
        pass
