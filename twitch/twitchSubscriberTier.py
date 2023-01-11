from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchSubscriberTier(Enum):

    TIER_ONE = auto()
    TIER_TWO = auto()
    TIER_THREE = auto()

    @classmethod
    def fromStr(ctls, text: Optional[str]):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == '1000':
            return TwitchSubscriberTier.TIER_ONE
        elif text == '2000':
            return TwitchSubscriberTier.TIER_TWO
        elif text == '3000':
            return TwitchSubscriberTier.TIER_THREE
        else:
            raise ValueError(f'unknown TwitchSubscriberTier: \"{text}\"')
