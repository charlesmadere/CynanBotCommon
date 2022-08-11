from typing import Optional

import aiohttp

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class NetworkClientProvider():

    def __init__(
        self,
        timeoutSeconds: int = 8
    ):
        if not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 2 or timeoutSeconds > 15:
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        self.__timeoutSeconds: int = timeoutSeconds
        self.__clientSession: Optional[aiohttp.ClientSession] = None

    async def get(self) -> aiohttp.ClientSession:
        if self.__clientSession is None:
            self.__clientSession = aiohttp.ClientSession(
                cookie_jar = aiohttp.DummyCookieJar(),
                timeout = aiohttp.ClientTimeout(total = self.__timeoutSeconds)
            )

        return self.__clientSession
