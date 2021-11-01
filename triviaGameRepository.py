import re
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.triviaModels import (AbsTriviaQuestion,
                                             MultipleChoiceTriviaQuestion,
                                             QuestionAnswerTriviaQuestion,
                                             TriviaType,
                                             TrueFalseTriviaQuestion)
    from CynanBotCommon.triviaRepository import TriviaRepository
    from CynanBotCommon.triviaScoreRepository import TriviaScoreRepository
except:
    import utils
    from triviaModels import (AbsTriviaQuestion, MultipleChoiceTriviaQuestion,
                              QuestionAnswerTriviaQuestion, TriviaType,
                              TrueFalseTriviaQuestion)
    from triviaRepository import TriviaRepository
    from triviaScoreRepository import TriviaScoreRepository


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

    def setAnswered(self):
        self.__isAnswered = None
        self.__answerTime = None
        self.__userIdThatRedeemed = None
        self.__userNameThatRedeemed = None

    def setTriviaQuestion(self, triviaQuestion: AbsTriviaQuestion):
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        self.__triviaQuestion = triviaQuestion

    def startNewTriviaGame(
        self,
        userIdThatRedeemed: str,
        userNameThatRedeemed: str
    ):
        if not utils.isValidStr(userIdThatRedeemed):
            raise ValueError(f'userIdThatRedeemed argument is malformed: \"{userIdThatRedeemed}\"')
        elif not utils.isValidStr(userNameThatRedeemed):
            raise ValueError(f'userNameThatRedeemed argument is malformed: \"{userNameThatRedeemed}\"')

        self.__isAnswered = False
        self.__answerTime = datetime.utcnow()
        self.__userIdThatRedeemed = userIdThatRedeemed
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
        triviaRepository: TriviaRepository,
        triviaScoreRepository: TriviaScoreRepository
    ):
        if triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')
        elif triviaScoreRepository is None:
            raise ValueError(f'triviaScoreRepository argument is malformed: \"{triviaScoreRepository}\"')

        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaScoreRepository: TriviaScoreRepository = triviaScoreRepository
        self.__states: Dict[str, State] = dict()
        self.__fullWordAnswerRegEx: Pattern = re.compile(r"\w+|\d+", re.IGNORECASE)
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r"[a-z]", re.IGNORECASE)

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

        if self.__checkAnswer(answer, triviaQuestion):
            self.__triviaScoreRepository.incrementTotalWins(twitchChannel, userId)
            return TriviaGameCheckResult.CORRECT_ANSWER
        else:
            self.__triviaScoreRepository.incrementTotalLosses(twitchChannel, userId)
            return TriviaGameCheckResult.INCORRECT_ANSWER

    def __checkAnswer(self, answer: str, triviaQuestion: AbsTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        if not utils.isValidStr(answer):
            return False

        if triviaQuestion.getTriviaType() is TriviaType.MULTIPLE_CHOICE:
            return self.__checkAnswerMultipleChoice(answer, triviaQuestion)
        elif triviaQuestion.getTriviaType() is TriviaType.QUESTION_ANSWER:
            return self.__checkAnswerQuestionAnswer(answer, triviaQuestion)
        elif triviaQuestion.getTriviaType() is TriviaType.TRUE_FALSE:
            return self.__checkAnswerTrueFalse(answer, triviaQuestion)
        else:
            raise RuntimeError(f'Unsupported TriviaType: \"{triviaQuestion.getTriviaType()}\"')

    def __checkAnswerMultipleChoice(self, answer: str, triviaQuestion: MultipleChoiceTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        answer = self.__applyAnswerCleanup(answer)

        if not utils.isValidStr(answer) or len(answer) != 1:
            return False
        elif self.__multipleChoiceAnswerRegEx.fullmatch(answer) is None:
            return False

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        index = ord(answer.upper()) % 65

        return index in triviaQuestion.getCorrectAnswerOrdinals()

    def __checkAnswerQuestionAnswer(self, answer: str, triviaQuestion: QuestionAnswerTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        cleanedAnswer = self.__applyAnswerCleanup(answer)
        correctAnswers = triviaQuestion.getCorrectAnswers()

        for correctAnswer in correctAnswers:
            cleanedCorrectAnswer = self.__applyAnswerCleanup(correctAnswer)

            # This if statement prevents a potentially really weird edge case of the correctanswer
            # being something that is dropped completely from the string in the applyAnswerCleanup()
            # method. So here, we have to fall back to just checking the raw answer strings, as we
            # have nothing else to go on.
            if utils.isValidStr(cleanedCorrectAnswer) and cleanedAnswer == cleanedCorrectAnswer:
                return True
            elif answer.lower() == correctAnswer.lower():
                return True

        return False

    def __checkAnswerTrueFalse(self, answer: str, triviaQuestion: TrueFalseTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        answer = self.__applyAnswerCleanup(answer)

        if not utils.isValidStr(answer):
            return False

        answerBool = utils.strToBool(answer)
        return answerBool in triviaQuestion.getCorrectAnswerBools()

    def fetchTrivia(
        self,
        twitchChannel: str,
        isLocalTriviaRepositoryEnabled: bool = False
    ) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(isLocalTriviaRepositoryEnabled):
            raise ValueError(f'isLocalTriviaRepositoryEnabled argument is malformed: \"{isLocalTriviaRepositoryEnabled}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            state = State(twitchChannel = twitchChannel.lower())
            self.__states[twitchChannel.lower()] = state
        else:
            state.setAnswered()

        triviaQuestion = self.__triviaRepository.fetchTrivia(
            isLocalTriviaRepositoryEnabled = isLocalTriviaRepositoryEnabled
        )

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
            return True

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

    def startNewTriviaGame(
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
            raise RuntimeError(f'there is no trivia game State available for Twitch channel \"{twitchChannel}\"')
        elif state.getTriviaQuestion() is None:
            raise RuntimeError(f'there is no trivia question available for Twitch channel \"{twitchChannel}\"')

        state.startNewTriviaGame(
            userIdThatRedeemed = userId,
            userNameThatRedeemed = userName
        )
