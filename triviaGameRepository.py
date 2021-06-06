import re
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.triviaRepository import (AbsTriviaQuestion,
                                                 TriviaRepository)
except:
    import utils
    from triviaRepository import AbsTriviaQuestion, TriviaRepository


class State():

    def __init__(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__triviaQuestion: AbsTriviaQuestion = None
        self.__isAnswered: bool = None
        self.__answerTime: datetime = None
        self.__twitchChannel: str = twitchChannel
        self.__userIdThatRedeemed: str = None
        self.__userNameThatRedeemed: str = None

    def getAnswerTime(self) -> datetime:
        return self.__answerTime

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserIdThatRedeemed(self) -> str:
        return self.__userIdThatRedeemed

    def getUserNameThatRedeemed(self) -> str:
        return self.__userNameThatRedeemed

    def isAnswered(self) -> bool:
        isAnswered = self.__isAnswered
        return isAnswered is None or isAnswered

    def refreshAnswerTime(self):
        self.__isAnswered = False
        self.__answerTime = datetime.utcnow()

    def setAnswered(self):
        self.__isAnswered = None
        self.__answerTime = None
        self.__userIdThatRedeemed = None
        self.__userNameThatRedeemed = None

    def setTriviaQuestion(self, triviaQuestion: AbsTriviaQuestion):
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        self.__triviaQuestion = triviaQuestion

    def setUserIdThatRedeemed(self, userIdThatRedeemed: str):
        if not utils.isValidStr(userIdThatRedeemed):
            raise ValueError(f'userIdThatRedeemed argument is malformed: \"{userIdThatRedeemed}\"')

        self.__userIdThatRedeemed = userIdThatRedeemed

    def setUserNameThatRedeemed(self, userNameThatRedeemed: str):
        if not utils.isValidStr(userNameThatRedeemed):
            raise ValueError(f'userNameThatRedeemed argument is malformed: \"{userNameThatRedeemed}\"')

        self.__userNameThatRedeemed = userNameThatRedeemed


class TriviaGameCheckResult(Enum):

    ALREADY_ANSWERED = auto()
    CORRECT_ANSWER = auto()
    INCORRECT_ANSWER = auto()
    INVALID_USER = auto()
    NOT_READY = auto()


class TriviaGameRepository():

    def __init__(
        self,
        triviaRepository: TriviaRepository
    ):
        if triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')

        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__states: Dict[str, State] = dict()

    def __applyAnswerCleanup(self, text: str) -> str:
        if not utils.isValidStr(text):
            return ''

        text = text.lower()
        regexResult = re.findall("\w+|\d+", text)
        return ''.join(regexResult)

    def checkAnswer(
        self,
        answer: str,
        twitchChannel: str,
        userId: str,
        userName: str
    ) -> TriviaGameCheckResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            return TriviaGameCheckResult.NOT_READY

        triviaQuestion = state.getTriviaQuestion()
        isAnswered = state.isAnswered()
        userIdThatRedeemed = state.getUserIdThatRedeemed()
        userNameThatRedeemed = state.getUserNameThatRedeemed()

        if triviaQuestion is None or not utils.isValidStr(userIdThatRedeemed) or not utils.isValidStr(userNameThatRedeemed):
            return TriviaGameCheckResult.NOT_READY
        elif isAnswered:
            return TriviaGameCheckResult.ALREADY_ANSWERED
        elif userIdThatRedeemed.lower() != userId.lower() or userNameThatRedeemed.lower() != userName.lower():
            return TriviaGameCheckResult.INVALID_USER

        state.setAnswered()

        if self.__checkAnswerStrings(answer, triviaQuestion.getCorrectAnswer()):
            return TriviaGameCheckResult.CORRECT_ANSWER
        else:
            return TriviaGameCheckResult.INCORRECT_ANSWER

    def __checkAnswerStrings(self, answer: str, correctAnswer: str) -> bool:
        if not utils.isValidStr(correctAnswer):
            raise ValueError(f'correctAnswer argument is malformed: \"{correctAnswer}\"')

        if utils.isValidStr(answer) and correctAnswer.lower() == answer.lower():
            return True

        answer = self.__applyAnswerCleanup(answer)
        correctAnswer = self.__applyAnswerCleanup(correctAnswer)
        return answer == correctAnswer

    def fetchTrivia(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            state = State(twitchChannel = twitchChannel.lower())
            self.__states[twitchChannel.lower()] = state
        else:
            state.setAnswered()

        triviaQuestion = self.__triviaRepository.fetchTrivia()
        state.setTriviaQuestion(triviaQuestion)

        return triviaQuestion

    def getTrivia(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            return None

        return state.getTriviaQuestion()

    def isAnswered(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            return False

        return state.isAnswered()

    def isWithinAnswerWindow(self, seconds: int, twitchChannel: str) -> bool:
        if not utils.isValidNum(seconds):
            raise ValueError(f'seconds argument is malformed: \"{seconds}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            return False

        answerTime = state.getAnswerTime()
        if answerTime is None:
            return False

        return answerTime + timedelta(seconds = seconds) > datetime.utcnow()

    def setAnswered(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            return

        state.setAnswered()

    def setUserThatRedeemed(
        self,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            return

        state.refreshAnswerTime()
        state.setUserIdThatRedeemed(userId)
        state.setUserNameThatRedeemed(userName)
