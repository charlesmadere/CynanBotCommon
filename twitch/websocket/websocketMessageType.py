from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketMessageType(Enum):

    KEEP_ALIVE = auto()
    NOTIFICATION = auto()
    RECONNECT = auto()
    REVOCATION = auto()
    WELCOME = auto()

    @classmethod
    def fromStr(text: Optional[str]):
        if not utils.isValidStr(text):
            return None

        text = text.lower()

        if text == 'session_keepalive':
            return WebsocketMessageType.KEEP_ALIVE
        elif text == 'notification':
            return WebsocketMessageType.NOTIFICATION
        elif text == 'session_reconnect':
            return WebsocketMessageType.RECONNECT
        elif text == 'revocation':
            return WebsocketMessageType.REVOCATION
        elif text == 'session_welcome':
            return WebsocketMessageType.WELCOME
        else:
            return None
