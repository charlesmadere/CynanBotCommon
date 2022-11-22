from typing import Any, Dict, Optional

try:
    from CynanBotCommon.network.networkClientType import NetworkClientType
except:
    from network.networkClientType import NetworkClientType


class NetworkResponse():

    async def close(self):
        pass

    def getNetworkClientType(self) -> NetworkClientType:
        pass

    def getStatusCode(self) -> int:
        pass

    def getUrl(self) -> str:
        pass

    def isClosed(self) -> bool:
        pass

    async def json(self) -> Optional[Dict[str, Any]]:
        pass

    async def read(self) -> bytes:
        pass
