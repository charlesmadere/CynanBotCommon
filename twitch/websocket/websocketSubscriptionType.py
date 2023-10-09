from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketSubscriptionType(Enum):

    CHANNEL_POINTS_REDEMPTION = auto()
    CHANNEL_UPDATE = auto()
    CHEER = auto()
    FOLLOW = auto()
    RAID = auto()
    STREAM_OFFLINE = auto()
    STREAM_ONLINE = auto()
    SUBSCRIBE = auto()
    SUBSCRIPTION_GIFT = auto()
    SUBSCRIPTION_MESSAGE = auto()

    @classmethod
    def fromStr(cls, text: Optional[str]):
        if not utils.isValidStr(text):
            return None

        text = text.lower()

        if text == 'channel.cheer':
            return WebsocketSubscriptionType.CHEER
        elif text == 'channel.channel_points_custom_reward_redemption.add':
            return WebsocketSubscriptionType.CHANNEL_POINTS_REDEMPTION
        elif text == 'channel.update':
            return WebsocketSubscriptionType.CHANNEL_UPDATE
        elif text == 'channel.follow':
            return WebsocketSubscriptionType.FOLLOW
        elif text == 'channel.raid':
            return WebsocketSubscriptionType.RAID
        elif text == 'stream.offline':
            return WebsocketSubscriptionType.STREAM_OFFLINE
        elif text == 'stream.online':
            return WebsocketSubscriptionType.STREAM_ONLINE
        elif text == 'channel.subscribe':
            return WebsocketSubscriptionType.SUBSCRIBE
        elif text == 'channel.subscription.message':
            return WebsocketSubscriptionType.SUBSCRIPTION_MESSAGE
        elif text == 'channel.subscription.gift':
            return WebsocketSubscriptionType.SUBSCRIPTION_GIFT
        else:
            return None
