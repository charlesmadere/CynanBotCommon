from abc import ABC

try:
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
except:
    from trivia.triviaActionType import TriviaActionType


class AbsTriviaAction(ABC):

    def __init__(
        self,
        triviaActionType: TriviaActionType
    ):
        if triviaActionType is None:
            raise ValueError(f'triviaActionType argument is malformed: \"{triviaActionType}\"')

        self.__triviaActionType: TriviaActionType = triviaActionType

    def getTriviaActionType(self) -> TriviaActionType:
        return self.__triviaActionType
