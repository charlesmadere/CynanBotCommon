from typing import Optional

try:
    from CynanBotCommon.twitch.websocket.websocketFollowEvent import \
        WebsocketFollowEvent
    from CynanBotCommon.twitch.websocket.websocketSession import \
        WebsocketSession
    from CynanBotCommon.twitch.websocket.websocketSubscription import \
        WebsocketSubscription
except:
    from twitch.websocket.websocketFollowEvent import WebsocketFollowEvent
    from twitch.websocket.websocketSession import WebsocketSession
    from twitch.websocket.websocketSubscription import WebsocketSubscription


class WebsocketPayload():

    def __init__(
        self,
        followEvent: Optional[WebsocketFollowEvent] = None,
        session: Optional[WebsocketSession] = None,
        subscription: Optional[WebsocketSubscription] = None
    ):
        if followEvent is not None and not isinstance(followEvent, WebsocketFollowEvent):
            raise ValueError(f'followEvent argument is malformed: \"{followEvent}\"')
        elif session is not None and not isinstance(session, WebsocketSession):
            raise ValueError(f'session argument is malformed: \"{session}\"')
        elif subscription is not None and not isinstance(subscription, WebsocketSubscription):
            raise ValueError(f'subscription argument is malformed: \"{subscription}\"')

        self.__followEvent: Optional[WebsocketFollowEvent] = followEvent
        self.__session: Optional[WebsocketSession] = session
        self.__subscription: Optional[WebsocketSubscription] = subscription

    def getFollowEvent(self) -> Optional[WebsocketFollowEvent]:
        return self.__followEvent

    def getSession(self) -> Optional[WebsocketSession]:
        return self.__session

    def getSubscription(self) -> Optional[WebsocketSubscription]:
        return self.__subscription

    def isEmpty(self) -> bool:
        return self.__followEvent is None and self.__session is None and self.__subscription is None
