class BadTriviaAnswerException(Exception):

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
