from enum import Enum, auto


class TriviaEventType(Enum):

    ANSWER_CORRECT = auto()
    ANSWER_INCORRECT = auto()
    FAILED_TO_FETCH_QUESTION = auto()
    NEW_GAME = auto()
    OUT_OF_TIME = auto()
