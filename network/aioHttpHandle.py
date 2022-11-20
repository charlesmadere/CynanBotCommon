from typing import Any, Dict, Optional

import aiohttp

try:
    from network.aioHttpResponse import AioHttpResponse

    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
    from CynanBotCommon.network.networkResponse import NetworkResponse
except:
    from network.aioHttpResponse import AioHttpResponse
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle
    from network.networkResponse import NetworkResponse


class AioHttpHandle(NetworkHandle):

    def __init__(
        self,
        clientSession: aiohttp.ClientSession
    ):
        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        response = await self.__clientSession.get(
            url = url,
            headers = headers
        )

        return AioHttpResponse(
            response = response,
            url = url
        )

    def getNetworkClientType(self) -> NetworkClientType:
        return NetworkClientType.AIOHTTP

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        response = await self.__clientSession.post(
            url = url,
            headers = headers,
            json = json
        )

        return AioHttpResponse(
            response = response,
            url = url
        )
