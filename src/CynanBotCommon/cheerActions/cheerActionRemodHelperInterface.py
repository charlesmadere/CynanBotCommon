from abc import ABC, abstractmethod

try:
    from CynanBotCommon.cheerActions.cheerActionRemodData import \
        CheerActionRemodData
except:
    from cheerActions.cheerActionRemodData import CheerActionRemodData


class CheerActionRemodHelperInterface(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    async def submitRemodData(self, action: CheerActionRemodData):
        pass
