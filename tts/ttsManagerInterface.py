from abc import ABC, abstractmethod

try:
    from CynanBotCommon.users.userInterface import UserInterface
except:
    from users.userInterface import UserInterface


class TtsManagerInterface(ABC):

    @abstractmethod
    async def executeTts(self, user: UserInterface, message: str):
        pass
