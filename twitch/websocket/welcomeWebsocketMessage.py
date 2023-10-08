try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.twitch.websocket.absWebsocketMessage import \
        AbsWebsocketMessage
    from CynanBotCommon.twitch.websocket.websocketMessageType import \
        WebsocketMessageType
except:
    import utils

    from twitch.websocket.absWebsocketMessage import AbsWebsocketMessage
    from twitch.websocket.websocketMessageType import WebsocketMessageType


class WelcomeWebsocketMessage(AbsWebsocketMessage):

    def __init__(
        self
    ):
        pass

    def getMessageType(self) -> WebsocketMessageType:
        return WebsocketMessageType.WELCOME
