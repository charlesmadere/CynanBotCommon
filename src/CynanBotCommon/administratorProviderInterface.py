from abc import abstractmethod

try:
    from CynanBotCommon.clearable import Clearable
except:
    from clearable import Clearable


class AdministratorProviderInterface(Clearable):

    @abstractmethod
    async def getAdministratorUserId(self) -> str:
        pass

    @abstractmethod
    async def getAdministratorUserName(self) -> str:
        pass
