from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class AdditionalTriviaAnswers():

    def __init__(
        self,
        additionalAnswers: List[str],
        triviaId: str,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ):
        if not utils.areValidStrs(additionalAnswers):
            raise ValueError(f'additionalAnswers argument is malformed: \"{additionalAnswers}\"')
        elif not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')
        elif not isinstance(triviaType, TriviaType):
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        self.__additionalAnswers: List[str] = additionalAnswers
        self.__triviaId: str = triviaId
        self.__triviaSource: TriviaSource = triviaSource
        self.__triviaType: TriviaType = triviaType

    def getAdditionalAnswers(self) -> List[str]:
        return self.__additionalAnswers

    def getAdditionalAnswersLen(self) -> int:
        return len(self.__additionalAnswers)

    def getTriviaId(self) -> str:
        return self.__triviaId

    def getTriviaSource(self) -> TriviaSource:
        return self.__triviaSource

    def getTriviaType(self) -> TriviaType:
        return self.__triviaType
