from typing import Any, Dict, Optional

import requests
from requests.models import Response

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
    from CynanBotCommon.network.networkResponse import NetworkResponse
    from CynanBotCommon.network.requestsResponse import RequestsResponse
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from network.exceptions import GenericNetworkException
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle
    from network.networkResponse import NetworkResponse
    from network.requestsResponse import RequestsResponse
    from timber.timber import Timber


class RequestsHandle(NetworkHandle):

    def __init__(
        self,
        timber: Timber,
        timeoutSeconds: int = 8
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 2 or timeoutSeconds > 16:
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        self.__timber: Timber = timber
        self.__timeoutSeconds: int = timeoutSeconds

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        response: Optional[Response] = None

        try:
            response = requests.get(
                url = url,
                headers = headers,
                timeout = self.__timeoutSeconds
            )
        except Exception as e:
            self.__timber.log('RequestsHandle', f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"', e)
            raise GenericNetworkException(f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"')

        if response is None:
            raise GenericNetworkException(f'Received no response (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"')

        return RequestsResponse(
            response = response,
            url = url
        )

    def getNetworkClientType(self) -> NetworkClientType:
        return NetworkClientType.REQUESTS

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        response: Optional[Response] = None

        try:
            response = requests.post(
                url = url,
                headers = headers,
                json = json,
                timeout = self.__timeoutSeconds
            )
        except Exception as e:
            self.__timber.log('RequestsHandle', f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"', e)
            raise GenericNetworkException(f'Encountered network error (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"')

        if response is None:
            raise GenericNetworkException(f'Received no response (via {self.getNetworkClientType()}) when trying to hit URL \"{url}\" with headers \"{headers}\"')

        return RequestsResponse(
            response = response,
            url = url
        )
