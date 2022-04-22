from enum import Enum, auto


class TriviaActionType(Enum):

    CHECK_ANSWER = auto()
    START_NEW_GAME = auto()
    START_NEW_SUPER_GAME = auto()
