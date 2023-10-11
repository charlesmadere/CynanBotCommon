try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.twitch.websocket.websocketCondition import \
        WebsocketCondition
    from CynanBotCommon.twitch.websocket.websocketTransport import \
        WebsocketTransport
except:
    import utils

    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketTransport import WebsocketTransport


class TwitchEventSubRequest():

    def __init__(
        self,
        subscriptionType: str,
        version: str,
        condition: WebsocketCondition,
        transport: WebsocketTransport
    ):
        if not utils.isValidStr(subscriptionType):
            raise ValueError(f'subscriptionType argument is malformed: \"{subscriptionType}\"')
        elif not utils.isValidStr(version):
            raise ValueError(f'version argument is malformed: \"{version}\"')
        elif not isinstance(condition, WebsocketCondition):
            raise ValueError(f'condition argument is malformed: \"{condition}\"')
        elif not isinstance(transport, WebsocketTransport):
            raise ValueError(f'transport argument is malformed: \"{transport}\"')

        self.__subscriptionType: str = subscriptionType
        self.__version: str = version
        self.__condition: WebsocketCondition = condition
        self.__transport: WebsocketTransport = transport

    def getCondition(self) -> WebsocketCondition:
        return self.__condition

    def getSubscriptionType(self) -> str:
        return self.__subscriptionType

    def getTransport(self) -> WebsocketTransport:
        return self.__transport

    def getVersion(self) -> str:
        return self.__version
