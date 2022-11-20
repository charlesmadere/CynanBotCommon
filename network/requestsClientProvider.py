try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.network.networkHandle import NetworkHandle
    from CynanBotCommon.network.requestsHandle import RequestsHandle
except:
    import utils
    from network.networkClientProvider import NetworkClientProvider
    from network.networkHandle import NetworkHandle
    from network.requestsHandle import RequestsHandle


class RequestsClientProvider(NetworkClientProvider):

    def __init__(
        self,
        timeoutSeconds: int = 8
    ):
        if not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 2 or timeoutSeconds > 16:
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        self.__timeoutSeconds: int = timeoutSeconds

    async def get(self) -> NetworkHandle:
        return RequestsHandle(
            timeoutSeconds = self.__timeoutSeconds
        )
