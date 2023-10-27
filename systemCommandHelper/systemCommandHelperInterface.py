from abc import ABC, abstractmethod


class SystemCommandHelperInterface(ABC):

    @abstractmethod
    async def executeCommand(self, command: str):
        pass
