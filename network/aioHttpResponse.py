from typing import Any, Dict

import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkResponse import NetworkResponse
except:
    import utils
    from network.networkClientType import NetworkClientType
    from network.networkResponse import NetworkResponse


class AioHttpResponse(NetworkResponse):

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        url: str
    ):
        if response is None:
            raise ValueError(f'response argument is malformed: \"{response}\"')
        elif not utils.isValidStr(url):
            raise ValueError(f'url argument is malformed: \"{url}\"')

        self.__response: aiohttp.ClientResponse = response
        self.__url: str = url

        self.__isClosed: bool = False

    async def close(self):
        if self.__isClosed:
            return

        self.__isClosed = True
        self.__response.close()

    def getNetworkClientType(self) -> NetworkClientType:
        return NetworkClientType.AIOHTTP

    def getUrl(self) -> str:
        return self.__url

    async def json(self) -> Dict[str, Any]:
        return await self.__response.json()

    def statusCode(self) -> int:
        return self.__response.status
