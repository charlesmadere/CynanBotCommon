class NoTriviaMultipleChoiceResponsesException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TooFewTriviaMultipleChoiceResponsesException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TooManyTriviaFetchAttemptsException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class UnsupportedTriviaTypeException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
