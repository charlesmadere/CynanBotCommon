import asyncio
import re
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta, timezone
from queue import SimpleQueue
from typing import Dict, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.checkAnswerTriviaAction import \
        CheckAnswerTriviaAction
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.startNewGameTriviaAction import \
        StartNewGameTriviaAction
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
    from CynanBotCommon.trivia.triviaExceptions import \
        UnknownTriviaActionTypeException
    from CynanBotCommon.trivia.triviaGameCheckResult import \
        TriviaGameCheckResult
    from CynanBotCommon.trivia.triviaGameState import TriviaGameState
    from CynanBotCommon.trivia.triviaRepository import TriviaRepository
    from CynanBotCommon.trivia.triviaScoreRepository import \
        TriviaScoreRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.checkAnswerTriviaAction import CheckAnswerTriviaAction
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.startNewGameTriviaAction import StartNewGameTriviaAction
    from trivia.triviaActionType import TriviaActionType
    from trivia.triviaExceptions import UnknownTriviaActionTypeException
    from trivia.triviaGameCheckResult import TriviaGameCheckResult
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaRepository import TriviaRepository
    from trivia.triviaScoreRepository import TriviaScoreRepository
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TriviaGameRepository():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        timber: Timber,
        triviaRepository: TriviaRepository,
        triviaScoreRepository: TriviaScoreRepository,
        sleepTimeSeconds: float = 0.5
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')
        elif triviaScoreRepository is None:
            raise ValueError(f'triviaScoreRepository argument is malformed: \"{triviaScoreRepository}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 0.1 or sleepTimeSeconds > 5:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')

        self.__timber: Timber = timber
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaScoreRepository: TriviaScoreRepository = triviaScoreRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds

        self.__states: Dict[str, TriviaGameState] = dict()
        self.__fullWordAnswerRegEx: Pattern = re.compile(r"\w+|\d+", re.IGNORECASE)
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r"[a-z]", re.IGNORECASE)

        self.__actionQueue: SimpleQueue[AbsTriviaAction] = SimpleQueue()
        eventLoop.create_task(self.__startActionLoop())

    async def __applyAnswerCleanup(self, text: str) -> str:
        if not utils.isValidStr(text):
            return ''

        text = text.lower()
        regexResult = self.__fullWordAnswerRegEx.findall(text)
        return ''.join(regexResult)

    async def checkAnswer(
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

        if await self.__checkAnswer(answer, triviaQuestion):
            return TriviaGameCheckResult.CORRECT_ANSWER
        else:
            return TriviaGameCheckResult.INCORRECT_ANSWER

    async def __checkAnswer(self, answer: str, triviaQuestion: AbsTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        if not utils.isValidStr(answer):
            return False

        if triviaQuestion.getTriviaType() is TriviaType.MULTIPLE_CHOICE:
            return await self.__checkAnswerMultipleChoice(answer, triviaQuestion)
        elif triviaQuestion.getTriviaType() is TriviaType.QUESTION_ANSWER:
            return await self.__checkAnswerQuestionAnswer(answer, triviaQuestion)
        elif triviaQuestion.getTriviaType() is TriviaType.TRUE_FALSE:
            return await self.__checkAnswerTrueFalse(answer, triviaQuestion)
        else:
            raise RuntimeError(f'Unsupported TriviaType: \"{triviaQuestion.getTriviaType()}\"')

    async def __checkAnswerMultipleChoice(self, answer: str, triviaQuestion: MultipleChoiceTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        answer = await self.__applyAnswerCleanup(answer)

        if not utils.isValidStr(answer) or len(answer) != 1:
            return False
        elif self.__multipleChoiceAnswerRegEx.fullmatch(answer) is None:
            return False

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        index = ord(answer.upper()) % 65

        return index in triviaQuestion.getCorrectAnswerOrdinals()

    async def __checkAnswerQuestionAnswer(self, answer: str, triviaQuestion: QuestionAnswerTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        cleanedAnswer = await self.__applyAnswerCleanup(answer)
        correctAnswers = triviaQuestion.getCorrectAnswers()

        for correctAnswer in correctAnswers:
            cleanedCorrectAnswer = await self.__applyAnswerCleanup(correctAnswer)

            # This if statement prevents a potentially really weird edge case of the correctanswer
            # being something that is dropped completely from the string in the applyAnswerCleanup()
            # method. So here, we have to fall back to just checking the raw answer strings, as we
            # have nothing else to go on.
            if utils.isValidStr(cleanedCorrectAnswer) and cleanedAnswer == cleanedCorrectAnswer:
                return True
            elif answer.lower() == correctAnswer.lower():
                return True

        return False

    async def __checkAnswerTrueFalse(
        self,
        answer: str,
        triviaQuestion: TrueFalseTriviaQuestion
    ) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        answer = await self.__applyAnswerCleanup(answer)

        if not utils.isValidStr(answer):
            return False

        answerBool = utils.strToBool(answer)
        return answerBool in triviaQuestion.getCorrectAnswerBools()

    async def fetchTrivia(
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

        triviaQuestion = await self.__triviaRepository.fetchTrivia(
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

    async def __handleActionCheckAnswer(self, action: CheckAnswerTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = self.__states.get(action.getTwitchChannel().lower())
        if state is None:
            
            return

        # TODO

        pass

    async def __handleActionStartNewGame(self, action: StartNewGameTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_GAME}: \"{action.getTriviaActionType()}\"')

        # TODO

        pass

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

    async def __startActionLoop(self):
        while True:
            while not self.__actionQueue.empty():
                action = self.__actionQueue.get()

                if action.getTriviaActionType() is TriviaActionType.CHECK_ANSWER:
                    await self.__handleActionCheckAnswer(action)
                elif action.getTriviaActionType() is TriviaActionType.START_NEW_GAME:
                    await self.__handleActionStartNewGame(action)
                else:
                    raise UnknownTriviaActionTypeException(f'Unknown TriviaActionType: \"{action.getTriviaActionType()}\"')

            await asyncio.sleep(self.__sleepTimeSeconds)

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

    def submitAction(self, action: AbsTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        self.__actionQueue.put(action)
