from enum import Enum, auto


class TriviaEventType(Enum):

    CORRECT_ANSWER = auto()
    FAILED_TO_FETCH_QUESTION = auto()
    GAME_ALREADY_IN_PROGRESS = auto()
    GAME_NOT_READY = auto()
    INCORRECT_ANSWER = auto()
    NEW_GAME = auto()
    OUT_OF_TIME = auto()
    TOO_LATE_TO_ANSWER = auto()
    WRONG_USER = auto()
