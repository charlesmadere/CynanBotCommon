from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import \
        NoTriviaCorrectAnswersException
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import NoTriviaCorrectAnswersException
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class QuestionAnswerTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[str],
        cleanedCorrectAnswers: List[str],
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
            raise NoTriviaCorrectAnswersException(f'correctAnswers argument is malformed: \"{correctAnswers}\"')
        elif not utils.areValidStrs(cleanedCorrectAnswers):
            raise NoTriviaCorrectAnswersException(f'cleanedCorrectAnswers argument is malformed: \"{cleanedCorrectAnswers}\"')

        self.__correctAnswers: List[str] = correctAnswers
        self.__cleanedCorrectAnswers: List[str] = cleanedCorrectAnswers

    def getCorrectAnswers(self) -> List[str]:
        return utils.copyStrList(self.__correctAnswers)

    def getCleanedCorrectAnswers(self) -> List[str]:
        return utils.copyStrList(self.__cleanedCorrectAnswers)

    def getPrompt(self, delimiter: str = None) -> str:
        if self.hasCategory():
            return f'(category is \"{self.getCategory()}\") {self.getQuestion()}'
        else:
            return self.getQuestion()

    def getResponses(self) -> List[str]:
        return list()
