import re
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.triviaRepository import (AbsTriviaQuestion,
                                                 TriviaRepository, TriviaType)
except:
    import utils
    from triviaRepository import (AbsTriviaQuestion, TriviaRepository,
                                  TriviaType)


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
        self.__fullWordAnswerRegEx: Pattern = re.compile("\w+|\d+")
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile("[a-zA-Z]")

    def __applyAnswerCleanup(self, text: str) -> str:
        if not utils.isValidStr(text):
            return ''

        text = text.lower()
        regexResult = self.__fullWordAnswerRegEx.findall(text)
        return ''.join(regexResult)

    def checkAnswer(
        self,
        answer: str,
        twitchChannel: str,
        userId: str
    ) -> TriviaGameCheckResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

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
        elif userIdThatRedeemed.lower() != userId.lower():
            return TriviaGameCheckResult.INVALID_USER

        state.setAnswered()

        if self.__checkAnswerStrings(answer, triviaQuestion):
            return TriviaGameCheckResult.CORRECT_ANSWER
        else:
            return TriviaGameCheckResult.INCORRECT_ANSWER

    def __checkAnswerStrings(self, answer: str, triviaQuestion: AbsTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        correctAnswer = triviaQuestion.getCorrectAnswer()

        if utils.isValidStr(answer) and correctAnswer.lower() == answer.lower():
            return True

        answer = self.__applyAnswerCleanup(answer)
        correctAnswer = self.__applyAnswerCleanup(correctAnswer)

        if answer == correctAnswer:
            return True
        elif triviaQuestion.getTriviaType() is not TriviaType.MULTIPLE_CHOICE or not self.__isLetterAnswer(answer):
            return False

        responses = triviaQuestion.getResponses()

        if not utils.hasItems(responses):
            raise RuntimeError(f'Encountered a {TriviaType.MULTIPLE_CHOICE} trivia question that has no responses!')

        # This converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        index = ord(answer.upper()) % 65

        return index >= 0 and index < len(responses) and responses[index] == triviaQuestion.getCorrectAnswer()

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
            raise RuntimeError(f'there is no trivia game State available for Twitch channel \"{twitchChannel}\"!')

        triviaQuestion = state.getTriviaQuestion()
        if triviaQuestion is None:
            raise RuntimeError(f'there is no trivia question available for Twitch channel \"{twitchChannel}\"')

        return triviaQuestion

    def isAnswered(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            return False

        return state.isAnswered()

    def __isLetterAnswer(self, answer: str) -> bool:
        if not utils.isValidStr(answer) or len(answer) != 1:
            return False

        return self.__multipleChoiceAnswerRegEx.fullmatch(answer) is not None

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
