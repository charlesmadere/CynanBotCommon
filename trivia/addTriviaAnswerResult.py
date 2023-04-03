from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from trivia.triviaSource import TriviaSource


class AddTriviaAnswerResult():

    def __init__(
        self,
        additionalAnswers: List[str],
        triviaId: str,
        triviaSource: TriviaSource
    ):
        if not utils.areValidStrs(additionalAnswers):
            raise ValueError(f'additionalAnswers argument is malformed: \"{additionalAnswers}\"')
        elif not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        self.__additionalAnswers: List[str] = additionalAnswers
        self.__triviaId: str = triviaId
        self.__triviaSource: TriviaSource = triviaSource

    def getAdditionalAnswers(self) -> List[str]:
        return self.__additionalAnswers

    def getTriviaId(self) -> str:
        return self.__triviaId

    def getTriviaSource(self) -> TriviaSource:
        return self.__triviaSource
