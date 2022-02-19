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

    def toStr(self) -> str:
        if self is TriviaDifficulty.EASY:
            return 'easy'
        elif self is TriviaDifficulty.HARD:
            return 'hard'
        elif self is TriviaDifficulty.MEDIUM:
            return 'medium'
        elif self is TriviaDifficulty.UNKNOWN:
            return 'unknown'
        else:
            raise ValueError(f'unknown TriviaDifficulty: \"{self}\"')
