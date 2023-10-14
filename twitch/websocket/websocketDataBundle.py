try:
    from CynanBotCommon.twitch.websocket.websocketMetadata import \
        WebsocketMetadata
    from CynanBotCommon.twitch.websocket.websocketPayload import \
        WebsocketPayload
except:
    from twitch.websocket.websocketMetadata import WebsocketMetadata
    from twitch.websocket.websocketPayload import WebsocketPayload


class WebsocketDataBundle():

    def __init__(
        self,
        metadata: WebsocketMetadata,
        payload: WebsocketPayload
    ):
        if not isinstance(metadata, WebsocketMetadata):
            raise ValueError(f'metadata argument is malformed: \"{metadata}\"')
        if not isinstance(payload, WebsocketPayload):
            raise ValueError(f'payload argument is malformed: \"{payload}\"')

        self.__metadata: WebsocketMetadata = metadata
        self.__payload: WebsocketPayload = payload

    def getMetadata(self) -> WebsocketMetadata:
        return self.__metadata

    def getPayload(self) -> WebsocketPayload:
        return self.__payload
