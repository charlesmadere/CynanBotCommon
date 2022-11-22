from typing import Any, Dict, Optional

import aiohttp

try:
    from network.aioHttpResponse import AioHttpResponse

    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
    from CynanBotCommon.network.networkResponse import NetworkResponse
    from CynanBotCommon.timber.timber import Timber
except:
    from network.aioHttpResponse import AioHttpResponse
    from network.exceptions import GenericNetworkException
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle
    from network.networkResponse import NetworkResponse
    from timber.timber import Timber


class AioHttpHandle(NetworkHandle):

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        timber: Timber
    ):
        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: Timber = timber

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        response: Optional[aiohttp.ClientResponse] = None

        try:
            response = await self.__clientSession.get(
                url = url,
                headers = headers
            )
        except Exception as e:
            self.__timber.log('AioHttpHandle', f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"', e)
            raise GenericNetworkException(f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"')

        if response is None:
            raise GenericNetworkException(f'Received no response (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"')

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
        response: Optional[aiohttp.ClientResponse] = None

        try:
            response = await self.__clientSession.post(
                url = url,
                headers = headers,
                json = json
            )
        except Exception as e:
            self.__timber.log('AioHttpHandle', f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\" and json \"{json}\"', e)
            raise GenericNetworkException(f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\" and json \"{json}\"')

        if response is None:
            raise GenericNetworkException(f'Received no response (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\" and json \"{json}\"')

        return AioHttpResponse(
            response = response,
            url = url
        )
