from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketConditionStatus(Enum):

    CANCELED = auto()
    FULFILLED = auto()
    UNFULFILLED = auto()
    UNKNOWN = auto()

    @classmethod
    def fromStr(cls, text: Optional[str]):
        if not utils.isValidStr(text):
            return WebsocketConditionStatus.UNKNOWN

        text = text.lower()

        if text in ('canceled', 'cancelled'):
            return WebsocketConditionStatus.CANCELED
        elif text == 'fulfilled':
            return WebsocketConditionStatus.FULFILLED
        elif text == 'unfulfilled':
            return WebsocketConditionStatus.UNFULFILLED
        else:
            return WebsocketConditionStatus.UNKNOWN
