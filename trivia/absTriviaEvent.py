from abc import ABC

try:
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
except:
    from trivia.triviaEventType import TriviaEventType


class AbsTriviaEvent(ABC):

    def __init__(
        self,
        triviaEventType: TriviaEventType
    ):
        if triviaEventType is None:
            raise ValueError(f'triviaEventType argument is malformed: \"{triviaEventType}\"')

        self.__triviaEventType: TriviaEventType = triviaEventType

    def getTriviaEventType(self) -> TriviaEventType:
        return self.__triviaEventType
