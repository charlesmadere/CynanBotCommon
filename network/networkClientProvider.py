try:
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
except:
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle


class NetworkClientProvider():

    async def get(self) -> NetworkHandle:
        pass

    def getNetworkClientType(self) -> NetworkClientType:
        pass
