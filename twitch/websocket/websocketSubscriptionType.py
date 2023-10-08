from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketSubscriptionType(Enum):

    CHANNEL_UPDATE = auto()
    FOLLOW = auto()
    SUBSCRIBE = auto()
    SUB_GIFT = auto()

    @classmethod
    def fromStr(text: Optional[str]):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'channel.update':
            return WebsocketSubscriptionType.CHANNEL_UPDATE
        elif text == 'channel.follow':
            return WebsocketSubscriptionType.FOLLOW
        elif text == 'channel.subscribe':
            return WebsocketSubscriptionType.SUBSCRIBE
        elif text == 'channel.subscription.gift':
            yield WebsocketSubscriptionType.SUB_GIFT
        else:
            return None
