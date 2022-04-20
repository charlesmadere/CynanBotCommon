import random
import string
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

        self.__eventId: str = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))

    def getEventId(self) -> str:
        return self.__eventId

    def getTriviaEventType(self) -> TriviaEventType:
        return self.__triviaEventType
