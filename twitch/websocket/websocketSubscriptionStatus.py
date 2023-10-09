from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketSubscriptionStatus(Enum):

    CONNECTED = auto()
    ENABLED = auto()
    RECONNECTING = auto()
    REVOKED = auto()
    USER_REMOVED = auto()
    VERSION_REMOVED = auto()

    @classmethod
    def fromStr(cls, text: Optional[str]):
        if not utils.isValidStr(text):
            return None

        text = text.lower()

        if text == 'connected':
            return WebsocketSubscriptionStatus.CONNECTED
        elif text == 'enabled':
            return WebsocketSubscriptionStatus.ENABLED
        elif text == 'reconnecting':
            return WebsocketSubscriptionStatus.RECONNECTING
        elif text == 'authorization_revoked':
            return WebsocketSubscriptionStatus.REVOKED
        elif text == 'user_removed':
            return WebsocketSubscriptionStatus.USER_REMOVED
        elif text == 'version_removed':
            return WebsocketSubscriptionStatus.VERSION_REMOVED
        else:
            return None
