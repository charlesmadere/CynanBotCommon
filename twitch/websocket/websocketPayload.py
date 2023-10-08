try:
    from CynanBotCommon.twitch.websocket.websocketSubscription import \
        WebsocketSubscription
except:
    from twitch.websocket.websocketSubscription import WebsocketSubscription


class WebsocketPayload():

    def __init__(
        self,
        subscription: WebsocketSubscription
    ):
        if not isinstance(subscription, WebsocketSubscription):
            raise ValueError(f'subscription argument is malformed: \"{subscription}\"')

        self.__subscription: WebsocketSubscription = subscription

    def getSubscription(self) -> WebsocketSubscription:
        return self.__subscription
