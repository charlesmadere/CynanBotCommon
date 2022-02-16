from enum import Enum, auto


class TriviaGameCheckResult(Enum):

    ALREADY_ANSWERED = auto()
    CORRECT_ANSWER = auto()
    INCORRECT_ANSWER = auto()
    INVALID_USER = auto()
    NOT_READY = auto()
