from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class BannedWordCheckType(Enum):

    ANYWHERE = auto()
    EXACT_MATCH = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'anywhere':
            return BannedWordCheckType.ANYWHERE
        elif text == 'exact_match':
            return BannedWordCheckType.EXACT_MATCH
        else:
            raise ValueError(f'unknown BannedWordCheckType: \"{text}\"')
