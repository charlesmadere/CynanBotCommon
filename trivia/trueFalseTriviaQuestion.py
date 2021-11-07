from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class TrueFalseTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[bool],
        category: str,
        _id: str,
        question: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource
    ):
        super().__init__(
            category = category,
            _id = _id,
            question = question,
            triviaDifficulty = triviaDifficulty,
            triviaSource = triviaSource,
            triviaType = TriviaType.TRUE_FALSE
        )

        if not utils.areValidBools(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')

        self.__correctAnswers: List[bool] = correctAnswers

    def getCorrectAnswers(self) -> List[str]:
        correctAnswers: List[str] = list()

        for correctAnswer in self.__correctAnswers:
            correctAnswers.append(str(correctAnswer).lower())

        return correctAnswers

    def getCorrectAnswerBools(self) -> List[bool]:
        return self.__correctAnswers

    def getPrompt(self, delimiter: str = None) -> str:
        return f'True or false! {self.getQuestion()}'

    def getResponses(self) -> List[str]:
        return [ str(True).lower(), str(False).lower() ]
