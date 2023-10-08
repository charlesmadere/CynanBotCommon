from abc import ABC, abstractmethod

try:
    from CynanBotCommon.twitch.websocket.websocketMessageType import \
        WebsocketMessageType
    from CynanBotCommon.twitch.websocket.websocketMetadata import \
        WebsocketMetadata
except:
    from twitch.websocket.websocketMessageType import WebsocketMessageType
    from twitch.websocket.websocketMetadata import WebsocketMetadata


class AbsWebsocketMessage(ABC):

    def __init__(self, metadata: WebsocketMetadata):
        if not isinstance(metadata, WebsocketMetadata):
            raise ValueError(f'metadata argument is malformed: \"{metadata}\"')

        self.__metadata: WebsocketMetadata = metadata

    @abstractmethod
    def getMessageType(self) -> WebsocketMessageType:
        pass

    def getMetadata(self) -> WebsocketMetadata:
        return self.__metadata
