from typing import Any, Dict, Optional

import requests

try:
    from network.requestsResponse import RequestsResponse

    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkHandle import NetworkHandle
    from CynanBotCommon.network.networkResponse import NetworkResponse
except:
    import utils
    from network.networkClientType import NetworkClientType
    from network.networkHandle import NetworkHandle
    from network.networkResponse import NetworkResponse
    from network.requestsResponse import RequestsResponse


class RequestsHandle(NetworkHandle):

    def __init__(
        self,
        timeoutSeconds: int = 8
    ):
        if not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 2 or timeoutSeconds > 16:
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        self.__timeoutSeconds: int = timeoutSeconds

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        response = requests.get(
            url = url,
            headers = headers,
            timeout = self.__timeoutSeconds
        )

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
        response = requests.post(
            url = url,
            headers = headers,
            json = json,
            timeout = self.__timeoutSeconds
        )

        return RequestsResponse(
            response = response,
            url = url
        )
