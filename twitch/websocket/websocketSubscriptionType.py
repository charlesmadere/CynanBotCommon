from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketSubscriptionType(Enum):

    CHANNEL_UPDATE = auto()
    FOLLOW = auto()
    STREAMS_ONLINE = auto()
    SUBSCRIBE = auto()
    SUB_GIFT = auto()

    @classmethod
    def fromStr(cls, text: Optional[str]):
        if not utils.isValidStr(text):
            return None

        text = text.lower()

        if text == 'channel.update':
            return WebsocketSubscriptionType.CHANNEL_UPDATE
        elif text == 'channel.follow':
            return WebsocketSubscriptionType.FOLLOW
        elif text == 'streams.online':
            return WebsocketSubscriptionType.STREAMS_ONLINE
        elif text == 'channel.subscribe':
            return WebsocketSubscriptionType.SUBSCRIBE
        elif text == 'channel.subscription.gift':
            return WebsocketSubscriptionType.SUB_GIFT
        else:
            return None
