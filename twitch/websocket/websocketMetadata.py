try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.twitch.websocket.websocketMessageType import \
        WebsocketMessageType
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
except:
    import utils
    from simpleDateTime import SimpleDateTime

    from twitch.websocket.websocketMessageType import WebsocketMessageType
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType


class WebsocketMetadata():

    def __init__(
        self,
        subscriptionVersion: int,
        messageTimestamp: SimpleDateTime,
        messageId: str,
        messageType: WebsocketMessageType,
        subscriptionType: WebsocketSubscriptionType
    ):
        if not utils.isValidInt(subscriptionVersion):
            raise ValueError(f'subscriptionVersion argument is malformed: \"{subscriptionVersion}\"')
        elif not utils.isValidStr(messageId):
            raise ValueError(f'messageId argument is malformed: \"{messageId}\"')
        elif not isinstance(messageTimestamp, SimpleDateTime):
            raise ValueError(f'messageTimestamp argument is malformed: \"{messageTimestamp}\"')
        elif not isinstance(messageType, WebsocketMessageType):
            raise ValueError(f'messageType argument is malformed: \"{messageType}\"')
        elif not isinstance(subscriptionType, WebsocketSubscriptionType):
            raise ValueError(f'subscriptionType argument is malformed: \"{subscriptionType}\"')

        self.__subscriptionVersion: int = subscriptionVersion
        self.__messageTimestamp: SimpleDateTime = messageTimestamp
        self.__messageId: str = messageId
        self.__messageType: WebsocketMessageType = messageType
        self.__subscriptionType: WebsocketSubscriptionType = subscriptionType

    def getMessageId(self) -> str:
        return self.__messageId

    def getMessageTimestamp(self) -> SimpleDateTime:
        return self.__messageTimestamp

    def getMessageType(self) -> WebsocketMessageType:
        return self.__messageType

    def getSubscriptionType(self) -> WebsocketSubscriptionType:
        return self.__subscriptionType

    def getSubscriptionVersion(self) -> int:
        return self.__subscriptionVersion
