from datetime import datetime, timedelta
from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.triviaRepository import (TriviaRepository,
                                                 TriviaResponse)
except:
    import utils
    from triviaRepository import TriviaRepository, TriviaResponse


class TriviaGameCheckResult(Enum):

    ALREADY_ANSWERED = auto()
    CORRECT = auto()
    INCORRECT = auto()
    INVALID_USER_ID = auto()
    NOT_READY = auto()


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
        self.__userIdThatRedeemed = None
        self.__answerTime = None

    def check(self, answer: str, userId: str) -> TriviaGameCheckResult:
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        triviaResponse = self.__triviaResponse
        isAnswered = self.__isAnswered
        userIdThatRedeemed = self.__userIdThatRedeemed

        if triviaResponse is None or not utils.isValidStr(userIdThatRedeemed):
            return TriviaGameCheckResult.NOT_READY
        elif isAnswered:
            return TriviaGameCheckResult.ALREADY_ANSWERED
        elif userIdThatRedeemed.lower() != userId.lower():
            return TriviaGameCheckResult.INVALID_USER_ID

        self.setAnswered()
        correctAnswer = triviaResponse.getCorrectAnswer()

        if utils.isValidStr(answer) and correctAnswer.lower() == answer.lower():
            return TriviaGameCheckResult.CORRECT
        else:
            return TriviaGameCheckResult.INCORRECT

    def fetchTrivia(self) -> TriviaResponse:
        triviaResponse = self.__triviaRepository.fetchTrivia()

        if self.__triviaResponse is None:
            self.__isAnswered = False
        elif self.__triviaResponse != triviaResponse and self.__triviaResponse.getQuestion() != triviaResponse.getQuestion():
            self.__isAnswered = False

        if not self.__isAnswered:
            self.__userIdThatRedeemed = None

        self.__answerTime = datetime.utcnow()
        self.__triviaResponse = triviaResponse
        return triviaResponse

    def isAnswered(self) -> bool:
        return self.__isAnswered

    def isWithinAnswerWindow(self, seconds: int) -> bool:
        if not utils.isValidNum(seconds):
            raise ValueError(f'seconds argument is malformed: \"{seconds}\"')

        answerTime = self.__answerTime

        if answerTime is None:
            return False

        return answerTime + timedelta(seconds = seconds) > datetime.utcnow()

    def setAnswered(self):
        self.__isAnswered = True
        self.__userIdThatRedeemed = None

    def setUserIdThatRedeemed(self, userIdThatRedeemed: str):
        if not utils.isValidStr(userIdThatRedeemed):
            raise ValueError(f'userIdThatRedeemed argument is malformed: \"{userIdThatRedeemed}\"')

        self.__userIdThatRedeemed = userIdThatRedeemed
