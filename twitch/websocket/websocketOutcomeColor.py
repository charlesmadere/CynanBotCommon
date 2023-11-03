from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils
    

class WebsocketOutcomeColor(Enum):

    BLUE = auto()
    PINK = auto()

    def fromStr(cls, text: Optional[str]):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower

        if text == 'blue':
            return WebsocketOutcomeColor.BLUE
        elif text == 'pink':
            return WebsocketOutcomeColor.PINK
        else:
            raise ValueError(f'unknown WebsocketOutcomeColor: \"{text}\"')
