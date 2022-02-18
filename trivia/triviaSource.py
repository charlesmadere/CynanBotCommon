from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaSource(Enum):

    BONGO = auto()
    J_SERVICE = auto()
    LOCAL_TRIVIA_REPOSITORY = auto()
    OPEN_TRIVIA_DATABASE = auto()
    WILL_FRY_TRIVIA_API = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'bongo':
            return TriviaSource.BONGO
        elif text == 'j_service':
            return TriviaSource.J_SERVICE
        elif text == 'local_trivia':
            return TriviaSource.LOCAL_TRIVIA_REPOSITORY
        elif text == 'open_trivia':
            return TriviaSource.OPEN_TRIVIA_DATABASE
        elif text == 'will_fry_trivia':
            return TriviaSource.WILL_FRY_TRIVIA_API
        else:
            raise ValueError(f'unknown TriviaSource: \"{text}\"')

    def toStr(self) -> str:
        if self is TriviaSource.BONGO:
            return 'BONGO'
        elif self is TriviaSource.J_SERVICE:
            return 'J_SERVICE'
        elif self is TriviaSource.LOCAL_TRIVIA_REPOSITORY:
            return 'LOCAL_TRIVIA_REPOSITORY'
        elif self is TriviaSource.OPEN_TRIVIA_DATABASE:
            return 'OPEN_TRIVIA_DATABASE'
        elif self is TriviaSource.WILL_FRY_TRIVIA_API:
            return 'WILL_FRY_TRIVIA_API'
        else:
            raise ValueError(f'unknown TriviaSource: \"{self}\"')
