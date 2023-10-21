from typing import Any, Dict

try:
    from CynanBotCommon.twitch.websocket.websocketCondition import \
        WebsocketCondition
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from CynanBotCommon.twitch.websocket.websocketTransport import \
        WebsocketTransport
except:
    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from twitch.websocket.websocketTransport import WebsocketTransport


# This class intends to directly correspond to Twitch's "Create EventSub Subscription" API:
# https://dev.twitch.tv/docs/api/reference/#create-eventsub-subscription
class TwitchEventSubRequest():

    def __init__(
        self,
        condition: WebsocketCondition,
        subscriptionType: WebsocketSubscriptionType,
        transport: WebsocketTransport
    ):
        if not isinstance(condition, WebsocketCondition):
            raise ValueError(f'condition argument is malformed: \"{condition}\"')
        elif not isinstance(subscriptionType, WebsocketSubscriptionType):
            raise ValueError(f'subscriptionType argument is malformed: \"{subscriptionType}\"')
        elif not isinstance(transport, WebsocketTransport):
            raise ValueError(f'transport argument is malformed: \"{transport}\"')

        self.__condition: WebsocketCondition = condition
        self.__subscriptionType: WebsocketSubscriptionType = subscriptionType
        self.__transport: WebsocketTransport = transport

    def getCondition(self) -> WebsocketCondition:
        return self.__condition

    def getSubscriptionType(self) -> WebsocketSubscriptionType:
        return self.__subscriptionType

    def getTransport(self) -> WebsocketTransport:
        return self.__transport

    def __repr__(self) -> str:
        jsonDictionary = self.toJson()
        return f'{jsonDictionary}'

    def toJson(self) -> Dict[Any, Any]:
        return {
            'condition': {
                'broadcaster_user_id': self.__condition.requireBroadcasterUserId()
            },
            'transport': {
                'method': self.__transport.getMethod().toStr(),
                'session_id': self.__transport.requireSessionId()
            },
            'type': self.__subscriptionType.toStr(),
            'version': self.__subscriptionType.getVersion()
        }
