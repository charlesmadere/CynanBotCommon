from enum import Enum, auto


class TriviaEventType(Enum):

    CORRECT_ANSWER = auto()
    FAILED_TO_FETCH_QUESTION = auto()
    GAME_ALREADY_IN_PROGRESS = auto()
    GAME_NOT_READY = auto()
    GAME_OUT_OF_TIME = auto()
    INCORRECT_ANSWER = auto()
    NEW_GAME = auto()
    NEW_SUPER_GAME = auto()
    SUPER_GAME_ALREADY_IN_PROGRESS = auto()
    SUPER_GAME_CORRECT_ANSWER = auto()
    SUPER_GAME_OUT_OF_TIME = auto()
    TOO_LATE_TO_ANSWER = auto()
    WRONG_USER = auto()
