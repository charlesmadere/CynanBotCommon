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
        connectedAt: SimpleDateTime,
        sessionId: str,
        method: WebsocketTransportMethod
    ):
        if not isinstance(connectedAt, SimpleDateTime):
            raise ValueError(f'connectedAt argument is malformed: \"{connectedAt}\"')
        elif not utils.isValidStr(sessionId):
            raise ValueError(f'sessionId argument is malformed: \"{sessionId}\"')
        elif not isinstance(method, WebsocketTransportMethod):
            raise ValueError(f'method argument is malformed: \"{method}\"')

        self.__connectedAt: SimpleDateTime = connectedAt
        self.__sessionId: str = sessionId
        self.__method: WebsocketTransportMethod = method

    def getConnectedAt(self) -> str:
        return self.__connectedAt

    def getMethod(self) -> WebsocketTransportMethod:
        return self.__method

    def getSessionId(self) -> str:
        return self.__sessionId
