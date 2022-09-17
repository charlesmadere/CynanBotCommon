from asyncio import AbstractEventLoop
from typing import Optional

import aiohttp

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class NetworkClientProvider():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        timeoutSeconds: int = 8
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 2 or timeoutSeconds > 15:
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        self.__eventLoop: AbstractEventLoop = eventLoop
        self.__timeoutSeconds: int = timeoutSeconds
        self.__clientSession: Optional[aiohttp.ClientSession] = None

    async def get(self) -> aiohttp.ClientSession:
        if self.__clientSession is None:
            self.__clientSession = aiohttp.ClientSession(
                loop = self.__eventLoop,
                cookie_jar = aiohttp.DummyCookieJar(),
                timeout = aiohttp.ClientTimeout(total = self.__timeoutSeconds)
            )

        return self.__clientSession
