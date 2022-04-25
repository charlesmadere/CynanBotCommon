import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from queue import SimpleQueue
from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.checkAnswerTriviaAction import \
        CheckAnswerTriviaAction
    from CynanBotCommon.trivia.correctAnswerTriviaEvent import \
        CorrectAnswerTriviaEvent
    from CynanBotCommon.trivia.failedToFetchQuestionTriviaEvent import \
        FailedToFetchQuestionTriviaEvent
    from CynanBotCommon.trivia.gameAlreadyInProgressTriviaEvent import \
        GameAlreadyInProgressTriviaEvent
    from CynanBotCommon.trivia.gameNotReadyCheckAnswerTriviaEvent import \
        GameNotReadyCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.incorrectAnswerTriviaEvent import \
        IncorrectAnswerTriviaEvent
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.newGameTriviaEvent import NewGameTriviaEvent
    from CynanBotCommon.trivia.outOfTimeCheckAnswerTriviaEvent import \
        OutOfTimeCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.startNewGameTriviaAction import \
        StartNewGameTriviaAction
    from CynanBotCommon.trivia.startNewSuperGameTriviaAction import \
        StartNewSuperGameTriviaAction
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
    from CynanBotCommon.trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from CynanBotCommon.trivia.triviaExceptions import (
        BadTriviaAnswerException, TooManyTriviaFetchAttemptsException,
        UnknownTriviaActionTypeException, UnsupportedTriviaTypeException)
    from CynanBotCommon.trivia.triviaGameState import TriviaGameState
    from CynanBotCommon.trivia.triviaRepository import TriviaRepository
    from CynanBotCommon.trivia.triviaScoreRepository import \
        TriviaScoreRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
    from CynanBotCommon.trivia.wrongUserCheckAnswerTriviaEvent import \
        WrongUserCheckAnswerTriviaEvent
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.checkAnswerTriviaAction import CheckAnswerTriviaAction
    from trivia.correctAnswerTriviaEvent import CorrectAnswerTriviaEvent
    from trivia.failedToFetchQuestionTriviaEvent import \
        FailedToFetchQuestionTriviaEvent
    from trivia.gameAlreadyInProgressTriviaEvent import \
        GameAlreadyInProgressTriviaEvent
    from trivia.gameNotReadyCheckAnswerTriviaEvent import \
        GameNotReadyCheckAnswerTriviaEvent
    from trivia.incorrectAnswerTriviaEvent import IncorrectAnswerTriviaEvent
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.newGameTriviaEvent import NewGameTriviaEvent
    from trivia.outOfTimeCheckAnswerTriviaEvent import \
        OutOfTimeCheckAnswerTriviaEvent
    from trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.startNewGameTriviaAction import StartNewGameTriviaAction
    from trivia.startNewSuperGameTriviaAction import \
        StartNewSuperGameTriviaAction
    from trivia.triviaActionType import TriviaActionType
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaExceptions import (BadTriviaAnswerException,
                                         TooManyTriviaFetchAttemptsException,
                                         UnknownTriviaActionTypeException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaRepository import TriviaRepository
    from trivia.triviaScoreRepository import TriviaScoreRepository
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion
    from trivia.wrongUserCheckAnswerTriviaEvent import \
        WrongUserCheckAnswerTriviaEvent


class TriviaGameMachine():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        timber: Timber,
        triviaAnswerCompiler: TriviaAnswerCompiler,
        triviaRepository: TriviaRepository,
        triviaScoreRepository: TriviaScoreRepository,
        sleepTimeSeconds: float = 0.5
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaAnswerCompiler is None:
            raise ValueError(f'triviaAnswerCompiler argument is malformed: \"{triviaAnswerCompiler}\"')
        elif triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')
        elif triviaScoreRepository is None:
            raise ValueError(f'triviaScoreRepository argument is malformed: \"{triviaScoreRepository}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 0.1 or sleepTimeSeconds > 5:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')

        self.__timber: Timber = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaScoreRepository: TriviaScoreRepository = triviaScoreRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds

        self.__states: Dict[str, TriviaGameState] = dict()
        self.__eventListener = None

        self.__actionQueue: SimpleQueue[AbsTriviaAction] = SimpleQueue()
        self.__eventQueue: SimpleQueue[AbsTriviaEvent] = SimpleQueue()
        eventLoop.create_task(self.__startActionLoop())
        eventLoop.create_task(self.__startEventLoop())

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
            raise UnsupportedTriviaTypeException(f'Unsupported TriviaType: \"{triviaQuestion.getTriviaType()}\"')

    async def __checkAnswerMultipleChoice(
        self,
        answer: str,
        triviaQuestion: MultipleChoiceTriviaQuestion
    ) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.MULTIPLE_CHOICE:
            raise RuntimeError(f'TriviaType is not {TriviaType.MULTIPLE_CHOICE}: \"{triviaQuestion.getTriviaType()}\"')

        answerOrdinal: int = None
        try:
            answerOrdinal = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal(answer)
        except BadTriviaAnswerException as e:
            self.__timber.log('TriviaGameMachine', f'Unable to convert multiple choice answer to ordinal: \"{answer}\": {e}')
            return False

        return answerOrdinal in triviaQuestion.getCorrectAnswerOrdinals()

    async def __checkAnswerQuestionAnswer(
        self,
        answer: str,
        triviaQuestion: QuestionAnswerTriviaQuestion
    ) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.QUESTION_ANSWER:
            raise RuntimeError(f'TriviaType is not {TriviaType.QUESTION_ANSWER}: \"{triviaQuestion.getTriviaType()}\"')

        cleanedAnswer = await self.__triviaAnswerCompiler.compileTextAnswer(answer)
        if not utils.isValidStr(cleanedAnswer):
            return False

        correctAnswers = triviaQuestion.getCorrectAnswers()

        for correctAnswer in correctAnswers:
            if correctAnswer == cleanedAnswer:
                return True

        return False

    async def __checkAnswerTrueFalse(
        self,
        answer: str,
        triviaQuestion: TrueFalseTriviaQuestion
    ) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.TRUE_FALSE:
            raise RuntimeError(f'TriviaType is not {TriviaType.TRUE_FALSE}: \"{triviaQuestion.getTriviaType()}\"')

        answerBool: bool = None
        try:
            answerBool = await self.__triviaAnswerCompiler.compileBoolAnswer(answer)
        except BadTriviaAnswerException as e:
            self.__timber.log('TriviaGameMachine', f'Unable to convert true false answer to bool: \"{answer}\": {e}')
            return False

        return answerBool in triviaQuestion.getCorrectAnswerBools()

    async def __handleActionCheckAnswer(self, action: CheckAnswerTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = self.__states.get(action.getTwitchChannel().lower())
        if state is None:
            self.__eventQueue.put(GameNotReadyCheckAnswerTriviaEvent(
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getUserId() != action.getUserId():
            self.__eventQueue.put(WrongUserCheckAnswerTriviaEvent(
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        now = datetime.now(timezone.utc)

        if state.getEndTime() < now:
            self.__eventQueue.put(OutOfTimeCheckAnswerTriviaEvent(
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        del self.__states[action.getTwitchChannel().lower()]

        if not await self.__checkAnswer(action.getAnswer(), state.getTriviaQuestion()):
            triviaScoreResult = await self.__triviaScoreRepository.incrementTotalLosses(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

            self.__eventQueue.put(IncorrectAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName(),
                triviaScoreResult = triviaScoreResult
            ))
            return

        triviaScoreResult = await self.__triviaScoreRepository.incrementTotalWins(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        self.__eventQueue.put(CorrectAnswerTriviaEvent(
            triviaQuestion = state.getTriviaQuestion(),
            pointsForWinning = state.getPointsForWinning(),
            answer = action.getAnswer(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName(),
            triviaScoreResult = triviaScoreResult
        ))

    async def __handleActionStartNewGame(self, action: StartNewGameTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_GAME}: \"{action.getTriviaActionType()}\"')

        state = self.__states.get(action.getTwitchChannel().lower())
        now = datetime.now(timezone.utc)

        if state is not None and state.getEndTime() < now:
            self.__eventQueue.put(GameAlreadyInProgressTriviaEvent(
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        triviaQuestion: AbsTriviaQuestion = None
        try:
            triviaQuestion = await self.__triviaRepository.fetchTrivia(
                twitchChannel = action.getTwitchChannel(),
                isJokeTriviaRepositoryEnabled = action.isJokeTriviaRepositoryEnabled()
            )
        except TooManyTriviaFetchAttemptsException as e:
            self.__timber.log('TriviaGameMachine', f'Reached limit on trivia fetch attempts without being able to successfully retrieve a question: {e}')

        if triviaQuestion is None:
            self.__eventQueue.put(FailedToFetchQuestionTriviaEvent(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        state = TriviaGameState(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        )

        self.__states[action.getTwitchChannel().lower()] = state

        self.__eventQueue.put(NewGameTriviaEvent(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        ))

    async def __handleActionStartNewSuperGame(self, action: StartNewSuperGameTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_SUPER_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_SUPER_GAME}: \"{action.getTriviaActionType()}\"')

        # TODO
        pass

    async def __refreshStatusOfLiveGames(self):
        if not utils.hasItems(self.__states):
            return

        now = datetime.now(timezone.utc)
        statesToRemove: List[TriviaGameState] = list()

        for state in self.__states.values():
            if state is not None and state.getEndTime() < now:
                statesToRemove.append(state)

        if not utils.hasItems(statesToRemove):
            return

        for state in statesToRemove:
            del self.__states[state.getTwitchChannel().lower()]

            triviaScoreResult = await self.__triviaScoreRepository.incrementTotalLosses(
                twitchChannel = state.getTwitchChannel(),
                userId = state.getUserId()
            )

            self.__eventQueue.put(OutOfTimeTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                gameId = state.getGameId(),
                twitchChannel = state.getTwitchChannel(),
                userId = state.getUserId(),
                userName = state.getUserName(),
                triviaScoreResult = triviaScoreResult
            ))

    def setEventListener(self, listener):
        self.__eventListener = listener

    async def __startActionLoop(self):
        while True:
            while not self.__actionQueue.empty():
                action = self.__actionQueue.get()

                if action.getTriviaActionType() is TriviaActionType.CHECK_ANSWER:
                    await self.__handleActionCheckAnswer(action)
                elif action.getTriviaActionType() is TriviaActionType.START_NEW_GAME:
                    await self.__handleActionStartNewGame(action)
                elif action.getTriviaActionType() is TriviaActionType.START_NEW_SUPER_GAME:
                    await self.__handleActionStartNewSuperGame(action)
                else:
                    raise UnknownTriviaActionTypeException(f'Unknown TriviaActionType: \"{action.getTriviaActionType()}\"')

            if utils.hasItems(self.__states):
                await self.__refreshStatusOfLiveGames()

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __startEventLoop(self):
        while True:
            eventListener = self.__eventListener

            if eventListener is not None:
                while not self.__eventQueue.empty():
                    event = self.__eventQueue.get()
                    await eventListener(event)

            await asyncio.sleep(self.__sleepTimeSeconds)

    def submitAction(self, action: AbsTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        self.__actionQueue.put(action)
