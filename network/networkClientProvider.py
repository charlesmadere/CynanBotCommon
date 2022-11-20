try:
    from CynanBotCommon.network.networkHandle import NetworkHandle
except:
    from network.networkHandle import NetworkHandle


class NetworkClientProvider():

    async def get(self) -> NetworkHandle:
        pass
