try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.twitch.websocket.websocketSubscriptionCondition import \
        WebsocketSubscriptionCondition
    from CynanBotCommon.twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
except:
    import utils
    from simpleDateTime import SimpleDateTime

    from twitch.websocket.websocketSubscriptionCondition import \
        WebsocketSubscriptionCondition
    from twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType


class WebsocketSubscription():

    def __init__(
        self,
        createdAt: SimpleDateTime,
        subscriptionId: str,
        condition: WebsocketSubscriptionCondition,
        status: WebsocketSubscriptionStatus,
        type: WebsocketSubscriptionType
    ):
        if not isinstance(createdAt, SimpleDateTime):
            raise ValueError(f'createdAt argument is malformed: \"{createdAt}\"')
        elif not utils.isValidStr(subscriptionId):
            raise ValueError(f'subscriptionId argument is malformed: \"{subscriptionId}\"')
        elif not isinstance(condition, WebsocketSubscriptionCondition):
            raise ValueError(f'condition argument is malformed: \"{condition}\"')
        elif not isinstance(status, WebsocketSubscriptionStatus):
            raise ValueError(f'status argument is malformed: \"{status}\"')
        elif not isinstance(type, WebsocketSubscriptionType):
            raise ValueError(f'type argument is malformed: \"{type}\"')

        self.__createdAt: SimpleDateTime = createdAt
        self.__subscriptionId: str = subscriptionId
        self.__condition: WebsocketSubscriptionCondition = condition
        self.__status: WebsocketSubscriptionStatus = status
        self.__type: WebsocketSubscriptionType = type

    def getCondition(self) -> WebsocketSubscriptionCondition:
        return self.__condition

    def getCreatedAt(self) -> SimpleDateTime:
        return self.__createdAt

    def getStatus(self) -> WebsocketSubscriptionStatus:
        return self.__status

    def getSubscriptionId(self) -> str:
        return self.__subscriptionId

    def getType(self) -> WebsocketSubscriptionType:
        return self.__type
