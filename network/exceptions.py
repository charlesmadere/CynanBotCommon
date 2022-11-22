class NetworkResponseIsClosedException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class GenericNetworkException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
