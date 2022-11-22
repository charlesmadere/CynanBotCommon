from typing import Any, Dict, Optional

from requests.models import Response

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import \
        NetworkResponseIsClosedException
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkResponse import NetworkResponse
except:
    import utils
    from network.exceptions import NetworkResponseIsClosedException
    from network.networkClientType import NetworkClientType
    from network.networkResponse import NetworkResponse


class RequestsResponse(NetworkResponse):

    def __init__(
        self,
        response: Response,
        url: str
    ):
        if response is None:
            raise ValueError(f'response argument is malformed: \"{response}\"')
        elif not utils.isValidStr(url):
            raise ValueError(f'url argument is malformed: \"{url}\"')

        self.__response: Response = response
        self.__url: str = url

        self.__isClosed: bool = False

    async def close(self):
        if self.__isClosed:
            return

        self.__isClosed = True
        self.__response.close()

    def getNetworkClientType(self) -> NetworkClientType:
        return NetworkClientType.REQUESTS

    def getStatusCode(self) -> int:
        self.__requireNotClosed()
        return self.__response.status_code

    def getUrl(self) -> str:
        return self.__url

    def isClosed(self) -> bool:
        return self.__isClosed

    async def json(self) -> Optional[Dict[str, Any]]:
        self.__requireNotClosed()
        return self.__response.json()

    async def read(self) -> bytes:
        self.__requireNotClosed()
        return self.__response.content

    def __requireNotClosed(self):
        if self.isClosed():
            raise NetworkResponseIsClosedException(f'This response has already been closed! ({self.getNetworkClientType()})')
