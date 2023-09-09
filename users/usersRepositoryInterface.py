from abc import ABC, abstractmethod
from typing import List

try:
    from CynanBotCommon.users.userInterface import UserInterface
except:
    from users.userInterface import UserInterface


class UsersRepositoryInterface(ABC):

    @abstractmethod
    async def addUser(self, handle: str):
        pass

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    def containsUser(self, handle: str) -> bool:
        pass

    @abstractmethod
    async def containsUserAsync(self, handle: str) -> bool:
        pass

    @abstractmethod
    def getUser(self, handle: str) -> UserInterface:
        pass

    @abstractmethod
    async def getUserAsync(self, handle: str) -> UserInterface:
        pass

    @abstractmethod
    def getUsers(self) -> List[UserInterface]:
        pass

    @abstractmethod
    async def getUsersAsync(self) -> List[UserInterface]:
        pass

    @abstractmethod
    async def removeUser(self, handle: str):
        pass

    @abstractmethod
    async def setUserEnabled(self, handle: str, enabled: bool):
        pass
