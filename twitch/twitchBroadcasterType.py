from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchBroadcasterType(Enum):

    AFFILIATE = auto()
    NORMAL = auto()
    PARTNER = auto()

    @classmethod
    def fromStr(ctls, text: Optional[str]):
        if not utils.isValidStr(text):
            return TwitchBroadcasterType.NORMAL

        text = text.lower()

        if text == 'affiliate':
            return TwitchBroadcasterType.AFFILIATE
        elif text == 'partner':
            return TwitchBroadcasterType.PARTNER
        else:
            return TwitchBroadcasterType.NORMAL
