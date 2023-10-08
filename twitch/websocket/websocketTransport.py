from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.twitch.websocket.websocketTransportMethod import \
        WebsocketTransportMethod
except:
    import utils
    from simpleDateTime import SimpleDateTime

    from twitch.websocket.websocketTransportMethod import \
        WebsocketTransportMethod


class WebsocketTransport():

    def __init__(
        self,
        connectedAt: Optional[SimpleDateTime],
        sessionId: str,
        method: WebsocketTransportMethod
    ):
        if connectedAt is not None and not isinstance(connectedAt, SimpleDateTime):
            raise ValueError(f'connectedAt argument is malformed: \"{connectedAt}\"')
        elif not utils.isValidStr(sessionId):
            raise ValueError(f'sessionId argument is malformed: \"{sessionId}\"')
        elif not isinstance(method, WebsocketTransportMethod):
            raise ValueError(f'method argument is malformed: \"{method}\"')

        self.__connectedAt: Optional[SimpleDateTime] = connectedAt
        self.__sessionId: str = sessionId
        self.__method: WebsocketTransportMethod = method

    def getConnectedAt(self) -> Optional[SimpleDateTime]:
        return self.__connectedAt

    def getMethod(self) -> WebsocketTransportMethod:
        return self.__method

    def getSessionId(self) -> str:
        return self.__sessionId
