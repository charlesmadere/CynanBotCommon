from typing import Any, Dict, Optional

try:
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkResponse import NetworkResponse
except:
    from network.networkClientType import NetworkClientType
    from network.networkResponse import NetworkResponse


class NetworkHandle():

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        pass

    def getNetworkClientType(self) -> NetworkClientType:
        pass

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> NetworkResponse:
        pass
