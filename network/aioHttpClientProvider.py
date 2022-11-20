from asyncio import AbstractEventLoop
from typing import Optional

import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.aioHttpHandle import AioHttpHandle
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.network.networkHandle import NetworkHandle
except:
    import utils
    from network.aioHttpHandle import AioHttpHandle
    from network.networkClientProvider import NetworkClientProvider
    from network.networkHandle import NetworkHandle


class AioHtttpClientProvider(NetworkClientProvider):

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        timeoutSeconds: int = 8
    ):
        if not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 2 or timeoutSeconds > 16:
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        self.__eventLoop: AbstractEventLoop = eventLoop
        self.__timeoutSeconds: int = timeoutSeconds

        self.__clientSession: Optional[aiohttp.ClientSession] = None

    async def get(self) -> NetworkHandle:
        clientSession = self.__clientSession

        if clientSession is None:
            clientSession = aiohttp.ClientSession(
                loop = self.__eventLoop,
                cookie_jar = aiohttp.DummyCookieJar(),
                timeout = aiohttp.ClientTimeout(total = self.__timeoutSeconds)
            )

            self.__clientSession = clientSession

        return AioHttpHandle(
            clientSession = clientSession
        )
