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


class QuestionAnswerTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[str],
        category: str,
        question: str,
        triviaId: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource
    ):
        super().__init__(
            category = category,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = triviaDifficulty,
            triviaSource = triviaSource,
            triviaType = TriviaType.QUESTION_ANSWER
        )

        if not utils.areValidStrs(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')

        self.__correctAnswers: List[str] = correctAnswers

    def getCorrectAnswers(self) -> List[str]:
        correctAnswers: List[str] = list()

        for correctAnswer in self.__correctAnswers:
            correctAnswers.append(correctAnswer)

        return correctAnswers

    def getPrompt(self, delimiter: str = None) -> str:
        if self.hasCategory():
            return f'(category is \"{self.getCategory()}\") {self.getQuestion()}'
        else:
            return self.getQuestion()

    def getResponses(self) -> List[str]:
        return list()
