from typing import Any, Dict, Optional

import aiohttp

try:
    from CynanBotCommon.network.aioHttpResponse import AioHttpResponse
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
    from CynanBotCommon.network.networkResponse import NetworkResponse
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    from network.aioHttpResponse import AioHttpResponse
    from network.exceptions import GenericNetworkException
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle
    from network.networkResponse import NetworkResponse
    from timber.timberInterface import TimberInterface


class AioHttpHandle(NetworkHandle):

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        timber: TimberInterface
    ):
        if not isinstance(clientSession, aiohttp.ClientSession):
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: TimberInterface = timber

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
            self.__timber.log('AioHttpHandle', f'Encountered network error (via {self.getNetworkClientType()}) when trying to get URL \"{url}\" with headers \"{headers}\": {e}', e)
            raise GenericNetworkException(f'Encountered network error (via {self.getNetworkClientType()}) when trying to get URL \"{url}\" with headers \"{headers}\": {e}')

        if response is None:
            self.__timber.log('AioHttpHandle', f'Received no response (via {self.getNetworkClientType()}) when trying to get URL \"{url}\" with headers \"{headers}\"')
            raise GenericNetworkException(f'Received no response (via {self.getNetworkClientType()}) when trying to get URL \"{url}\" with headers \"{headers}\"')

        return AioHttpResponse(
            response = response,
            url = url,
            timber = self.__timber
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
            self.__timber.log('AioHttpHandle', f'Encountered network error (via {self.getNetworkClientType()}) when trying to post URL \"{url}\" with headers \"{headers}\" and json \"{json}\": {e}', e)
            raise GenericNetworkException(f'Encountered network error (via {self.getNetworkClientType()}) when trying to post URL \"{url}\" with headers \"{headers}\" and json \"{json}\": {e}')

        if response is None:
            self.__timber.log('AioHttpHandle', f'Received no response (via {self.getNetworkClientType()}) when trying to post URL \"{url}\" with headers \"{headers}\" and json \"{json}\"')
            raise GenericNetworkException(f'Received no response (via {self.getNetworkClientType()}) when trying to post URL \"{url}\" with headers \"{headers}\" and json \"{json}\"')

        return AioHttpResponse(
            response = response,
            url = url,
            timber = self.__timber
        )
