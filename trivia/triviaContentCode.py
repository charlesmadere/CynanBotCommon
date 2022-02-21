from enum import Enum, auto


class TriviaContentCode(Enum):

    ANSWER_TOO_LONG = auto()
    CONTAINS_BANNED_WORD = auto()
    CONTAINS_EMPTY_STR = auto()
    CONTAINS_URL = auto()
    IS_NONE = auto()
    OK = auto()
    QUESTION_TOO_LONG = auto()
    REPEAT = auto()
