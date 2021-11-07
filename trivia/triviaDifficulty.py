from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaDifficulty(Enum):

    EASY = auto()
    HARD = auto()
    MEDIUM = auto()
    UNKNOWN = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            return TriviaDifficulty.UNKNOWN

        text = text.lower()

        if text == 'easy':
            return TriviaDifficulty.EASY
        elif text == 'hard':
            return TriviaDifficulty.HARD
        elif text == 'medium':
            return TriviaDifficulty.MEDIUM
        else:
            return TriviaDifficulty.UNKNOWN
