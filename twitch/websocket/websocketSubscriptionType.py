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
        elif text == 'channel.subscribe':
            return WebsocketSubscriptionType.SUBSCRIBE
        elif text == 'channel.subscription.gift':
            return WebsocketSubscriptionType.SUBSCRIPTION_GIFT
        elif text == 'channel.subscription.message':
            return WebsocketSubscriptionType.SUBSCRIPTION_MESSAGE
        else:
            return None

    def toStr(self) -> str:
        if self is WebsocketSubscriptionType.CHEER:
            return 'channel.cheer'
        elif self is WebsocketSubscriptionType.CHANNEL_POINTS_REDEMPTION:
            return 'channel.channel_points_custom_reward_redemption.add'
        elif self is WebsocketSubscriptionType.CHANNEL_UPDATE:
            return 'channel.update'
        elif self is WebsocketSubscriptionType.FOLLOW:
            return 'channel.follow'
        elif self is WebsocketSubscriptionType.RAID:
            return 'channel.raid'
        elif self is WebsocketSubscriptionType.SUBSCRIBE:
            return 'channel.subscribe'
        elif self is WebsocketSubscriptionType.SUBSCRIPTION_GIFT:
            return 'channel.subscription.gift'
        elif self is WebsocketSubscriptionType.SUBSCRIPTION_MESSAGE:
            return 'channel.subscription.message'
        else:
            raise RuntimeError(f'unknown WebsocketSubscriptionType: \"{self}\"')
