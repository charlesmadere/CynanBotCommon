from abc import ABC, abstractmethod


class AdministratorProviderInterface(ABC):

    @abstractmethod
    async def getAdministratorUserId(self) -> str:
        pass

    @abstractmethod
    async def getAdministratorUserName(self) -> str:
        pass
