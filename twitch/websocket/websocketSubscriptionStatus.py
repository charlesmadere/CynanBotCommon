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
        else:
            return None
