try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.twitch.websocket.websocketCondition import \
        WebsocketCondition
    from CynanBotCommon.twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from CynanBotCommon.twitch.websocket.websocketTransport import \
        WebsocketTransport
except:
    import utils
    from simpleDateTime import SimpleDateTime

    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from twitch.websocket.websocketTransport import WebsocketTransport


class WebsocketSubscription():

    def __init__(
        self,
        cost: int,
        createdAt: SimpleDateTime,
        subscriptionId: str,
        version: str,
        condition: WebsocketCondition,
        status: WebsocketSubscriptionStatus,
        subscriptionType: WebsocketSubscriptionType,
        transport: WebsocketTransport
    ):
        if not utils.isValidInt(cost):
            raise ValueError(f'cost argument is malformed: \"{cost}\"')
        elif not isinstance(createdAt, SimpleDateTime):
            raise ValueError(f'createdAt argument is malformed: \"{createdAt}\"')
        elif not utils.isValidStr(subscriptionId):
            raise ValueError(f'subscriptionId argument is malformed: \"{subscriptionId}\"')
        elif not utils.isValidStr(version):
            raise ValueError(f'version argument is malformed: \"{version}\"')
        elif not isinstance(condition, WebsocketCondition):
            raise ValueError(f'condition argument is malformed: \"{condition}\"')
        elif not isinstance(status, WebsocketSubscriptionStatus):
            raise ValueError(f'status argument is malformed: \"{status}\"')
        elif not isinstance(subscriptionType, WebsocketSubscriptionType):
            raise ValueError(f'subscriptionType argument is malformed: \"{subscriptionType}\"')
        elif not isinstance(transport, WebsocketTransport):
            raise ValueError(f'transport argument is malformed: \"{transport}\"')

        self.__cost: int = cost
        self.__createdAt: SimpleDateTime = createdAt
        self.__subscriptionId: str = subscriptionId
        self.__version: str = version
        self.__condition: WebsocketCondition = condition
        self.__status: WebsocketSubscriptionStatus = status
        self.__subscriptionType: WebsocketSubscriptionType = subscriptionType
        self.__transport: WebsocketTransport = transport

    def getCondition(self) -> WebsocketCondition:
        return self.__condition

    def getCost(self) -> int:
        return self.__cost

    def getCreatedAt(self) -> SimpleDateTime:
        return self.__createdAt

    def getStatus(self) -> WebsocketSubscriptionStatus:
        return self.__status

    def getSubscriptionId(self) -> str:
        return self.__subscriptionId

    def getSubscriptionType(self) -> WebsocketSubscriptionType:
        return self.__subscriptionType

    def getTransport(self) -> WebsocketTransport:
        return self.__transport

    def getVersion(self) -> str:
        return self.__version
