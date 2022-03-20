import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaGameCheckResult import \
        TriviaGameCheckResult
    from CynanBotCommon.trivia.triviaGameState import TriviaGameState
    from CynanBotCommon.trivia.triviaRepository import TriviaRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaGameCheckResult import TriviaGameCheckResult
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaRepository import TriviaRepository
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TriviaGameRepository():

    def __init__(
        self,
        timber: Timber,
        triviaRepository: TriviaRepository
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')

        self.__timber: Timber = timber
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__states: Dict[str, TriviaGameState] = dict()
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
            return TriviaGameCheckResult.CORRECT_ANSWER
        else:
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

    def __checkAnswerTrueFalse(
        self,
        answer: str,
        triviaQuestion: TrueFalseTriviaQuestion
    ) -> bool:
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
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            state = TriviaGameState(twitchChannel = twitchChannel.lower())
            self.__states[twitchChannel.lower()] = state
        else:
            state.setAnswered()

        triviaQuestion = self.__triviaRepository.fetchTrivia(
            twitchChannel = twitchChannel,
            isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
        )

        state.setTriviaQuestion(triviaQuestion)

        return triviaQuestion

    def getTrivia(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        state = self.__states.get(twitchChannel.lower())
        if state is None:
            raise RuntimeError(f'there is no TriviaGameState available for Twitch channel \"{twitchChannel}\"!')

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

        return answerTime + timedelta(seconds = seconds) > datetime.now(timezone.utc)

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
            raise RuntimeError(f'there is no TriviaGameState available for Twitch channel \"{twitchChannel}\"')
        elif state.getTriviaQuestion() is None:
            raise RuntimeError(f'there is no trivia question available for Twitch channel \"{twitchChannel}\"')

        self.__timber.log('TriviaGameRepository', f'Starting new trivia game for {userName}:{userId} in {twitchChannel}...')

        state.startNewTriviaGame(
            userIdThatRedeemed = userId,
            userNameThatRedeemed = userName
        )
