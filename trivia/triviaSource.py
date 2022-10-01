from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaSource(Enum):

    BONGO = auto()
    FUNTOON = auto()
    JOKE_TRIVIA_REPOSITORY = auto()
    J_SERVICE = auto()
    LORD_OF_THE_RINGS = auto()
    MILLIONAIRE = auto()
    OPEN_TRIVIA_DATABASE = auto()
    OPEN_TRIVIA_QA = auto()
    QUIZ_API = auto()
    TRIVIA_DATABASE = auto()
    WILL_FRY_TRIVIA = auto()
    WWTBAM = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'bongo':
            return TriviaSource.BONGO
        elif text == 'funtoon':
            return TriviaSource.FUNTOON
        elif text == 'joke_trivia_repository':
            return TriviaSource.JOKE_TRIVIA_REPOSITORY
        elif text == 'j_service':
            return TriviaSource.J_SERVICE
        elif text == 'lord_of_the_rings':
            return TriviaSource.LORD_OF_THE_RINGS
        elif text == 'millionaire':
            return TriviaSource.MILLIONAIRE
        elif text == 'open_trivia' or text == 'open_trivia_database':
            return TriviaSource.OPEN_TRIVIA_DATABASE
        elif text == 'open_trivia_qa':
            return TriviaSource.OPEN_TRIVIA_QA
        elif text == 'quiz_api':
            return TriviaSource.QUIZ_API
        elif text == 'trivia_database':
            return TriviaSource.TRIVIA_DATABASE
        elif text == 'will_fry_trivia' or text == 'will_fry_trivia_api':
            return TriviaSource.WILL_FRY_TRIVIA
        elif text == 'wwtbam':
            return TriviaSource.WWTBAM
        else:
            raise ValueError(f'unknown TriviaSource: \"{text}\"')

    def toStr(self) -> str:
        if self is TriviaSource.BONGO:
            return 'BONGO'
        elif self is TriviaSource.FUNTOON:
            return 'FUNTOON'
        elif self is TriviaSource.JOKE_TRIVIA_REPOSITORY:
            return 'JOKE_TRIVIA_REPOSITORY'
        elif self is TriviaSource.J_SERVICE:
            return 'J_SERVICE'
        elif self is TriviaSource.LORD_OF_THE_RINGS:
            return 'LORD_OF_THE_RINGS'
        elif self is TriviaSource.MILLIONAIRE:
            return 'MILLIONAIRE'
        elif self is TriviaSource.OPEN_TRIVIA_DATABASE:
            return 'OPEN_TRIVIA_DATABASE'
        elif self is TriviaSource.OPEN_TRIVIA_QA:
            return 'OPEN_TRIVIA_QA'
        elif self is TriviaSource.QUIZ_API:
            return 'QUIZ_API'
        elif self is TriviaSource.TRIVIA_DATABASE:
            return 'TRIVIA_DATABASE'
        elif self is TriviaSource.WILL_FRY_TRIVIA:
            return 'WILL_FRY_TRIVIA'
        elif self is TriviaSource.WWTBAM:
            return 'WWTBAM'
        else:
            raise ValueError(f'unknown TriviaSource: \"{self}\"')
