from typing import Any, Dict

try:
    from CynanBotCommon.network.networkClientType import NetworkClientType
except:
    from network.networkClientType import NetworkClientType


class NetworkResponse():

    async def close(self):
        pass

    def getNetworkClientType(self) -> NetworkClientType:
        pass

    def getUrl(self) -> str:
        pass

    def isClosed(self) -> bool:
        pass

    async def json(self) -> Dict[str, Any]:
        pass

    def statusCode(self) -> int:
        pass
