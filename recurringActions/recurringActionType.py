from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class RecurringActionType(Enum):

    SUPER_TRIVIA = auto()
    WEATHER = auto()
    WORD_OF_THE_DAY = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'super_trivia':
            return RecurringActionType.SUPER_TRIVIA
        elif text == 'weather':
            return RecurringActionType.WEATHER
        elif text == 'word_of_the_day':
            return RecurringActionType.WORD_OF_THE_DAY
        else:
            raise ValueError(f'unknown RecurringActionType: \"{text}\"')

    def getRecurringActionTimingMinutes(self) -> int:
        if self is RecurringActionType.SUPER_TRIVIA:
            return 10
        elif self is RecurringActionType.WEATHER:
            return 120
        elif self is RecurringActionType.WORD_OF_THE_DAY:
            return 60
        else:
            raise RuntimeError(f'unknown RecurringActionType: \"{self}\"')

    def toStr(self) -> str:
        if self is RecurringActionType.SUPER_TRIVIA:
            return 'super_trivia'
        elif self is RecurringActionType.WEATHER:
            return 'weather'
        elif self is RecurringActionType.WORD_OF_THE_DAY:
            return 'word_of_the_day'
        else:
            raise RuntimeError(f'unknown RecurringActionType: \"{self}\"')