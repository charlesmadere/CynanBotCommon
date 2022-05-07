class NoBearerTokenException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class NoChannelGuuidException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class StreamElementsNetworkException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
