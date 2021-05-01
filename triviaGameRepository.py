try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.triviaRepository import (TriviaRepository,
                                                 TriviaResponse)
except:
    import utils
    from triviaRepository import TriviaRepository, TriviaResponse


class TriviaGameRepository():

    def __init__(
        self,
        triviaRepository: TriviaRepository
    ):
        if triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')

        self.__triviaRepository = triviaRepository
        self.__triviaResponse = None
        self.__isAnswered = False

    def checkAnswer(self, answer: str) -> bool:
        if not utils.isValidStr(answer) or self.__isAnswered:
            return False

        triviaResponse = self.__triviaResponse

        if triviaResponse is None:
            return False

        self.__isAnswered = True
        correctAnswer = triviaResponse.getCorrectAnswer()
        return correctAnswer.lower() == answer.lower()

    def fetchTrivia(self) -> TriviaResponse:
        triviaResponse = self.__triviaRepository.fetchTrivia()

        if self.__triviaResponse is None:
            self.__isAnswered = False
        elif self.__triviaResponse != triviaResponse and self.__triviaResponse.getQuestion() != triviaResponse.getQuestion():
            self.__isAnswered = False

        self.__triviaResponse = triviaResponse
        return triviaResponse

    def isAnswered(self) -> bool:
        return self.__isAnswered

    def setAnswered(self):
        self.__isAnswered = True
