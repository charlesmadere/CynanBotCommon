try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
    from CynanBotCommon.network.requestsHandle import RequestsHandle
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from network.networkClientProvider import NetworkClientProvider
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle
    from network.requestsHandle import RequestsHandle
    from timber.timber import Timber


class RequestsClientProvider(NetworkClientProvider):

    def __init__(
        self,
        timber: Timber,
        timeoutSeconds: int = 8
    ):
        if not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 2 or timeoutSeconds > 16:
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        self.__timber: Timber = timber
        self.__timeoutSeconds: int = timeoutSeconds

    async def get(self) -> NetworkHandle:
        return RequestsHandle(
            timber = self.__timber,
            timeoutSeconds = self.__timeoutSeconds
        )

    def getNetworkClientType(self) -> NetworkClientType:
        return NetworkClientType.REQUESTS
