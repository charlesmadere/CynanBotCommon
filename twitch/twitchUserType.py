from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchUserType(Enum):

    ADMIN = auto()
    GLOBAL_MOD = auto()
    NORMAL = auto()
    STAFF = auto()

    @classmethod
    def fromStr(ctls, text: Optional[str]):
        if not utils.isValidStr(text):
            return TwitchUserType.NORMAL

        text = text.lower()

        if text == 'admin':
            return TwitchUserType.ADMIN
        elif text == 'global_mod':
            return TwitchUserType.GLOBAL_MOD
        elif text == 'staff':
            return TwitchUserType.STAFF
        else:
            return TwitchUserType.NORMAL
