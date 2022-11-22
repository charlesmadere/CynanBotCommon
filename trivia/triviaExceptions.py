from typing import Optional

try:
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    from trivia.triviaSource import TriviaSource


class BadTriviaAnswerException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class BadTriviaSessionTokenException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class GenericTriviaNetworkException(Exception):

    def __init__(
        self,
        triviaSource: TriviaSource,
        exception: Optional[Exception] = None
    ):
        super().__init__(triviaSource, exception)


class MalformedTriviaJsonException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class NoTriviaCorrectAnswersException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class NoTriviaMultipleChoiceResponsesException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class NoTriviaQuestionException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TooManyTriviaFetchAttemptsException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class UnknownTriviaActionTypeException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class UnknownTriviaGameTypeException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class UnsupportedTriviaTypeException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
