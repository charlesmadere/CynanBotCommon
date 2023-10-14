from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
except:
    import utils
    from simpleDateTime import SimpleDateTime

    from twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus


class WebsocketSession():

    def __init__(
        self,
        keepAliveTimeoutSeconds: int,
        connectedAt: SimpleDateTime,
        reconnectUrl: Optional[str],
        sessionId: str,
        status: WebsocketSubscriptionStatus
    ):
        if not utils.isValidInt(keepAliveTimeoutSeconds):
            raise ValueError(f'keepAliveTimeoutSeconds argument is malformed: \"{keepAliveTimeoutSeconds}\"')
        elif not isinstance(connectedAt, SimpleDateTime):
            raise ValueError(f'connectedAt argument is malformed: \"{connectedAt}\"')
        elif reconnectUrl is not None and not utils.isValidUrl(reconnectUrl):
            raise ValueError(f'reconnectUrl argument is malformed: \"{reconnectUrl}\"')
        elif not utils.isValidStr(sessionId):
            raise ValueError(f'sessionId argument is malformed: \"{sessionId}\"')
        elif not isinstance(status, WebsocketSubscriptionStatus):
            raise ValueError(f'status argument is malformed: \"{status}\"')

        self.__keepAliveTimeoutSeconds: int = keepAliveTimeoutSeconds
        self.__connectedAt: SimpleDateTime = connectedAt
        self.__reconnectUrl: Optional[str] = reconnectUrl
        self.__sessionId: str = sessionId
        self.__status: WebsocketSubscriptionStatus = status

    def getConnectedAt(self) -> SimpleDateTime:
        return self.__connectedAt

    def getKeepAliveTimeoutSeconds(self) -> int:
        return self.__keepAliveTimeoutSeconds

    def getReconnectUrl(self) -> Optional[str]:
        return self.__reconnectUrl

    def getSessionId(self) -> str:
        return self.__sessionId

    def getStatus(self) -> WebsocketSubscriptionStatus:
        return self.__status

    def __str__(self) -> str:
        return f'connectedAt=\"{self.__connectedAt}\", keepAliveTimeoutSeconds=\"{self.__keepAliveTimeoutSeconds}\", \
            reconnectUrl=\"{self.__reconnectUrl}\", sessionId=\"{self.__sessionId}\", status=\"{self.__status}\"'
