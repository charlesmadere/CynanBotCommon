from abc import ABC, abstractmethod

try:
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
except:
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle


class NetworkClientProvider(ABC):

    @abstractmethod
    async def get(self) -> NetworkHandle:
        pass

    @abstractmethod
    def getNetworkClientType(self) -> NetworkClientType:
        pass
