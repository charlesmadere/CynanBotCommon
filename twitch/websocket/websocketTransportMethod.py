from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketTransportMethod(Enum):

    WEBHOOK = auto()
    WEBSOCKET = auto()

    @classmethod
    def fromStr(cls, text: Optional[str]):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'webhook':
            return WebsocketTransportMethod.WEBHOOK
        elif text == 'websocket':
            return WebsocketTransportMethod.WEBSOCKET
        else:
            raise ValueError(f'unknown WebsocketTransportMethod: \"{text}\"')
