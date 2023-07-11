from enum import Enum, auto


class AddAutoWordOfTheDayLanguageResult(Enum):

    ADDED = auto()
    ALREADY_EXISTS = auto()
    ERROR = auto()
