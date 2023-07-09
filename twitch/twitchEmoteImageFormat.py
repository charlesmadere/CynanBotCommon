from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchEmoteImageFormat(Enum):

    ANIMATED = auto()
    DEFAULT = auto()
    STATIC = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'animated':
            return TwitchEmoteImageFormat.ANIMATED
        elif text == 'static':
            return TwitchEmoteImageFormat.STATIC
        else:
            raise RuntimeError(f'unknown TwitchEmoteImageFormat: \"{text}\"')
