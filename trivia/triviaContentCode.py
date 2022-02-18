from enum import Enum, auto


class TriviaContentCode(Enum):

    CONTAINS_BANNED_WORD = auto()
    CONTAINS_EMPTY_STR = auto()
    CONTAINS_URL = auto()
    IS_NONE = auto()
    OK = auto()
    REPEAT = auto()
