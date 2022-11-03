import asyncio
import queue
from asyncio import AbstractEventLoop
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from queue import SimpleQueue
from typing import Any, Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.absTriviaGameState import AbsTriviaGameState
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.checkAnswerTriviaAction import \
        CheckAnswerTriviaAction
    from CynanBotCommon.trivia.correctAnswerTriviaEvent import \
        CorrectAnswerTriviaEvent
    from CynanBotCommon.trivia.correctSuperAnswerTriviaEvent import \
        CorrectSuperAnswerTriviaEvent
    from CynanBotCommon.trivia.failedToFetchQuestionSuperTriviaEvent import \
        FailedToFetchQuestionSuperTriviaEvent
    from CynanBotCommon.trivia.failedToFetchQuestionTriviaEvent import \
        FailedToFetchQuestionTriviaEvent
    from CynanBotCommon.trivia.gameAlreadyInProgressTriviaEvent import \
        GameAlreadyInProgressTriviaEvent
    from CynanBotCommon.trivia.gameNotReadyCheckAnswerTriviaEvent import \
        GameNotReadyCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.incorrectAnswerTriviaEvent import \
        IncorrectAnswerTriviaEvent
    from CynanBotCommon.trivia.incorrectSuperAnswerTriviaEvent import \
        IncorrectSuperAnswerTriviaEvent
    from CynanBotCommon.trivia.invalidAnswerInputTriviaEvent import \
        InvalidAnswerInputTriviaEvent
    from CynanBotCommon.trivia.newQueuedSuperTriviaGameEvent import \
        NewQueuedSuperTriviaGameEvent
    from CynanBotCommon.trivia.newSuperTriviaGameEvent import \
        NewSuperTriviaGameEvent
    from CynanBotCommon.trivia.newTriviaGameEvent import NewTriviaGameEvent
    from CynanBotCommon.trivia.outOfTimeSuperTriviaEvent import \
        OutOfTimeSuperTriviaEvent
    from CynanBotCommon.trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from CynanBotCommon.trivia.queuedTriviaGameStore import \
        QueuedTriviaGameStore
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.startNewTriviaGameAction import \
        StartNewTriviaGameAction
    from CynanBotCommon.trivia.superGameNotReadyCheckAnswerTriviaEvent import \
        SuperGameNotReadyCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.superTriviaGameState import SuperTriviaGameState
    from CynanBotCommon.trivia.tooLateToAnswerCheckAnswerTriviaEvent import \
        TooLateToAnswerCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.tooLateToAnswerCheckSuperAnswerTriviaEvent import \
        TooLateToAnswerCheckSuperAnswerTriviaEvent
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
    from CynanBotCommon.trivia.triviaAnswerChecker import TriviaAnswerChecker
    from CynanBotCommon.trivia.triviaAnswerCheckResult import \
        TriviaAnswerCheckResult
    from CynanBotCommon.trivia.triviaEventListener import TriviaEventListener
    from CynanBotCommon.trivia.triviaExceptions import (
        TooManyTriviaFetchAttemptsException, UnknownTriviaActionTypeException,
        UnknownTriviaGameTypeException)
    from CynanBotCommon.trivia.triviaGameState import TriviaGameState
    from CynanBotCommon.trivia.triviaGameStore import TriviaGameStore
    from CynanBotCommon.trivia.triviaGameType import TriviaGameType
    from CynanBotCommon.trivia.triviaRepository import TriviaRepository
    from CynanBotCommon.trivia.triviaScoreRepository import \
        TriviaScoreRepository
    from CynanBotCommon.trivia.wrongUserCheckAnswerTriviaEvent import \
        WrongUserCheckAnswerTriviaEvent
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.absTriviaGameState import AbsTriviaGameState
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.checkAnswerTriviaAction import CheckAnswerTriviaAction
    from trivia.correctAnswerTriviaEvent import CorrectAnswerTriviaEvent
    from trivia.correctSuperAnswerTriviaEvent import \
        CorrectSuperAnswerTriviaEvent
    from trivia.failedToFetchQuestionSuperTriviaEvent import \
        FailedToFetchQuestionSuperTriviaEvent
    from trivia.failedToFetchQuestionTriviaEvent import \
        FailedToFetchQuestionTriviaEvent
    from trivia.gameAlreadyInProgressTriviaEvent import \
        GameAlreadyInProgressTriviaEvent
    from trivia.gameNotReadyCheckAnswerTriviaEvent import \
        GameNotReadyCheckAnswerTriviaEvent
    from trivia.incorrectAnswerTriviaEvent import IncorrectAnswerTriviaEvent
    from trivia.incorrectSuperAnswerTriviaEvent import \
        IncorrectSuperAnswerTriviaEvent
    from trivia.invalidAnswerInputTriviaEvent import \
        InvalidAnswerInputTriviaEvent
    from trivia.newQueuedSuperTriviaGameEvent import \
        NewQueuedSuperTriviaGameEvent
    from trivia.newSuperTriviaGameEvent import NewSuperTriviaGameEvent
    from trivia.newTriviaGameEvent import NewTriviaGameEvent
    from trivia.outOfTimeSuperTriviaEvent import OutOfTimeSuperTriviaEvent
    from trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from trivia.queuedTriviaGameStore import QueuedTriviaGameStore
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.startNewTriviaGameAction import StartNewTriviaGameAction
    from trivia.superGameNotReadyCheckAnswerTriviaEvent import \
        SuperGameNotReadyCheckAnswerTriviaEvent
    from trivia.superTriviaGameState import SuperTriviaGameState
    from trivia.tooLateToAnswerCheckAnswerTriviaEvent import \
        TooLateToAnswerCheckAnswerTriviaEvent
    from trivia.tooLateToAnswerCheckSuperAnswerTriviaEvent import \
        TooLateToAnswerCheckSuperAnswerTriviaEvent
    from trivia.triviaActionType import TriviaActionType
    from trivia.triviaAnswerChecker import TriviaAnswerChecker
    from trivia.triviaAnswerCheckResult import TriviaAnswerCheckResult
    from trivia.triviaEventListener import TriviaEventListener
    from trivia.triviaExceptions import (TooManyTriviaFetchAttemptsException,
                                         UnknownTriviaActionTypeException,
                                         UnknownTriviaGameTypeException)
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaGameStore import TriviaGameStore
    from trivia.triviaGameType import TriviaGameType
    from trivia.triviaRepository import TriviaRepository
    from trivia.triviaScoreRepository import TriviaScoreRepository
    from trivia.wrongUserCheckAnswerTriviaEvent import \
        WrongUserCheckAnswerTriviaEvent


class TriviaGameMachine():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        queuedTriviaGameStore: QueuedTriviaGameStore,
        timber: Timber,
        triviaAnswerChecker: TriviaAnswerChecker,
        triviaGameStore: TriviaGameStore,
        triviaRepository: TriviaRepository,
        triviaScoreRepository: TriviaScoreRepository,
        sleepTimeSeconds: float = 0.5
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif queuedTriviaGameStore is None:
            raise ValueError(f'queuedTriviaGameStore argument is malformed: \"{queuedTriviaGameStore}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaAnswerChecker is None:
            raise ValueError(f'triviaAnswerChecker argument is malformed: \"{triviaAnswerChecker}\"')
        elif triviaGameStore is None:
            raise ValueError(f'triviaGameStore argument is malformed: \"{triviaGameStore}\"')
        elif triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')
        elif triviaScoreRepository is None:
            raise ValueError(f'triviaScoreRepository argument is malformed: \"{triviaScoreRepository}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 0.25 or sleepTimeSeconds > 2:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')

        self.__queuedTriviaGameStore: QueuedTriviaGameStore = queuedTriviaGameStore
        self.__timber: Timber = timber
        self.__triviaAnswerChecker: TriviaAnswerChecker = triviaAnswerChecker
        self.__triviaGameStore: TriviaGameStore = triviaGameStore
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaScoreRepository: TriviaScoreRepository = triviaScoreRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds

        self.__mostRecentSuperTrivia: Dict[str, datetime] = defaultdict(lambda: datetime.now(timezone.utc) - timedelta(hours = 1))
        self.__eventListener: Optional[TriviaEventListener] = None
        self.__actionQueue: SimpleQueue[AbsTriviaAction] = SimpleQueue()
        self.__eventQueue: SimpleQueue[AbsTriviaEvent] = SimpleQueue()
        eventLoop.create_task(self.__startActionLoop())
        eventLoop.create_task(self.__startEventLoop())

    async def __beginQueuedGames(self):
        activeChannels = await self.__triviaGameStore.getTwitchChannelsWithActiveSuperGames()
        queuedSuperGames = await self.__queuedTriviaGameStore.popQueuedSuperGames(activeChannels)

        for queuedSuperGame in queuedSuperGames:
            self.__timber.log('TriviaGameMachine', f'Starting new queued super trivia game for \"{queuedSuperGame.getTwitchChannel()}\"')
            await self.__handleActionStartNewSuperTriviaGame(queuedSuperGame)

    async def __checkAnswer(
        self,
        answer: Optional[str],
        triviaQuestion: AbsTriviaQuestion,
        extras: Optional[Dict[str, Any]] = None
    ) -> TriviaAnswerCheckResult:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        return await self.__triviaAnswerChecker.checkAnswer(answer, triviaQuestion, extras)

    async def __handleActionCheckAnswer(self, action: CheckAnswerTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = await self.__triviaGameStore.getNormalGame(
            twitchChannel = action.getTwitchChannel(),
            userName = action.getUserName()
        )

        now = datetime.now(timezone.utc)

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
                triviaQuestion = state.getTriviaQuestion(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getEndTime() < now:
            await self.__triviaGameStore.removeNormalGame(
                twitchChannel = action.getTwitchChannel(),
                userName = action.getUserName()
            )

            triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaLosses(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

            self.__eventQueue.put(TooLateToAnswerCheckAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName(),
                triviaScoreResult = triviaScoreResult
            ))
            return

        checkResult = await self.__checkAnswer(
            answer = action.getAnswer(),
            triviaQuestion = state.getTriviaQuestion()
        )

        if checkResult is TriviaAnswerCheckResult.INVALID_INPUT:
            self.__eventQueue.put(InvalidAnswerInputTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        await self.__triviaGameStore.removeNormalGame(
            twitchChannel = action.getTwitchChannel(),
            userName = action.getUserName()
        )

        if checkResult is TriviaAnswerCheckResult.INCORRECT:
            triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaLosses(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

            self.__eventQueue.put(IncorrectAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName(),
                triviaScoreResult = triviaScoreResult
            ))
            return

        triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaWins(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        self.__eventQueue.put(CorrectAnswerTriviaEvent(
            triviaQuestion = state.getTriviaQuestion(),
            pointsForWinning = state.getPointsForWinning(),
            actionId = action.getActionId(),
            answer = action.getAnswer(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName(),
            triviaScoreResult = triviaScoreResult
        ))

    async def __handleActionCheckSuperAnswer(self, action: CheckAnswerTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_SUPER_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_SUPER_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = await self.__triviaGameStore.getSuperGame(action.getTwitchChannel())
        now = datetime.now(timezone.utc)

        if state is None:
            self.__eventQueue.put(SuperGameNotReadyCheckAnswerTriviaEvent(
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getEndTime() < now:
            self.__eventQueue.put(TooLateToAnswerCheckSuperAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if not state.isEligibleToAnswer(action.getUserName()):
            return

        state.incrementAnswerCount(action.getUserName())

        checkResult = await self.__checkAnswer(
            answer = action.getAnswer(),
            triviaQuestion = state.getTriviaQuestion(),
            extras = {
                'actionId': action.getActionId(),
                'twitchChannel': action.getTwitchChannel(),
                'userId': action.getUserId(),
                'userName': action.getUserName()
            }
        )

        # Below, we're intentionally ignoring TriviaAnswerCheckResult values that are not CORRECT.

        if checkResult is not TriviaAnswerCheckResult.CORRECT:
            self.__eventQueue.put(IncorrectSuperAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        await self.__triviaGameStore.removeSuperGame(action.getTwitchChannel())

        triviaScoreResult = await self.__triviaScoreRepository.incrementSuperTriviaWins(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        self.__eventQueue.put(CorrectSuperAnswerTriviaEvent(
            triviaQuestion = state.getTriviaQuestion(),
            pointsForWinning = state.getPointsForWinning(),
            pointsMultiplier = state.getPointsMultiplier(),
            actionId = action.getActionId(),
            answer = action.getAnswer(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName(),
            triviaScoreResult = triviaScoreResult
        ))

    async def __handleActionStartNewTriviaGame(self, action: StartNewTriviaGameAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_GAME}: \"{action.getTriviaActionType()}\"')

        now = datetime.now(timezone.utc)
        state = await self.__triviaGameStore.getNormalGame(
            twitchChannel = action.getTwitchChannel(),
            userName = action.getUserName()
        )

        if state is not None and state.getEndTime() >= now:
            self.__eventQueue.put(GameAlreadyInProgressTriviaEvent(
                gameId = state.getGameId(),
                actionId = action.getActionId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        triviaQuestion: Optional[AbsTriviaQuestion] = None
        try:
            triviaQuestion = await self.__triviaRepository.fetchTrivia(action.getTriviaFetchOptions())
        except TooManyTriviaFetchAttemptsException as e:
            self.__timber.log('TriviaGameMachine', f'Reached limit on trivia fetch attempts without being able to successfully retrieve a trivia question for \"{action.getTwitchChannel()}\": {e}')

        if triviaQuestion is None:
            self.__eventQueue.put(FailedToFetchQuestionTriviaEvent(
                actionId = action.getActionId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        state = TriviaGameState(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            actionId = action.getActionId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        )

        await self.__triviaGameStore.add(state)

        self.__eventQueue.put(NewTriviaGameEvent(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            actionId = action.getActionId(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        ))

    async def __handleActionStartNewSuperTriviaGame(self, action: StartNewSuperTriviaGameAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_SUPER_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_SUPER_GAME}: \"{action.getTriviaActionType()}\"')

        now = datetime.now(timezone.utc)
        state = await self.__triviaGameStore.getSuperGame(action.getTwitchChannel())
        isSuperTriviaGameCurrentlyInProgress = state is not None and state.getEndTime() >= now

        queueResult = await self.__queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = isSuperTriviaGameCurrentlyInProgress,
            action = action
        )

        if queueResult.getAmountAdded() >= 1:
            self.__timber.log('TriviaGameMachine', f'Queued new Super Trivia game(s) for \"{action.getTwitchChannel()}\": {queueResult.toStr()}')

            self.__eventQueue.put(NewQueuedSuperTriviaGameEvent(
                numberOfGames = queueResult.getAmountAdded(),
                pointsForWinning = action.getPointsForWinning(),
                pointsMultiplier = action.getPointsMultiplier(),
                secondsToLive = action.getSecondsToLive(),
                actionId = action.getActionId(),
                twitchChannel = action.getTwitchChannel()
            ))

        if isSuperTriviaGameCurrentlyInProgress:
            return

        triviaQuestion: Optional[AbsTriviaQuestion] = None
        try:
            triviaQuestion = await self.__triviaRepository.fetchTrivia(action.getTriviaFetchOptions())
        except TooManyTriviaFetchAttemptsException as e:
            self.__timber.log('TriviaGameMachine', f'Reached limit on trivia fetch attempts without being able to successfully retrieve a super trivia question for \"{action.getTwitchChannel()}\": {e}')

        if triviaQuestion is None:
            self.__eventQueue.put(FailedToFetchQuestionSuperTriviaEvent(
                actionId = action.getActionId(),
                twitchChannel = action.getTwitchChannel()
            ))
            return

        state = SuperTriviaGameState(
            triviaQuestion = triviaQuestion,
            perUserAttempts = action.getPerUserAttempts(),
            pointsForWinning = action.getPointsForWinning(),
            pointsMultiplier = action.getPointsMultiplier(),
            secondsToLive = action.getSecondsToLive(),
            actionId = action.getActionId(),
            twitchChannel = action.getTwitchChannel()
        )

        await self.__triviaGameStore.add(state)

        self.__eventQueue.put(NewSuperTriviaGameEvent(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            pointsMultiplier = action.getPointsMultiplier(),
            secondsToLive = action.getSecondsToLive(),
            actionId = action.getActionId(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
        ))

    async def __refreshStatusOfGames(self):
        await self.__removeDeadGames()
        await self.__beginQueuedGames()

    async def __removeDeadGames(self):
        now = datetime.now(timezone.utc)
        gameStates = await self.__triviaGameStore.getAll()
        gameStatesToRemove: List[AbsTriviaGameState] = list()

        for state in gameStates:
            if state.getEndTime() < now:
                gameStatesToRemove.append(state)

        for state in gameStatesToRemove:
            if state.getTriviaGameType() is TriviaGameType.NORMAL:
                normalGameState: TriviaGameState = state

                await self.__triviaGameStore.removeNormalGame(
                    twitchChannel = normalGameState.getTwitchChannel(),
                    userName = normalGameState.getUserName()
                )

                triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaLosses(
                    twitchChannel = normalGameState.getTwitchChannel(),
                    userId = normalGameState.getUserId()
                )

                self.__eventQueue.put(OutOfTimeTriviaEvent(
                    triviaQuestion = normalGameState.getTriviaQuestion(),
                    actionId = normalGameState.getActionId(),
                    gameId = normalGameState.getGameId(),
                    twitchChannel = normalGameState.getTwitchChannel(),
                    userId = normalGameState.getUserId(),
                    userName = normalGameState.getUserName(),
                    triviaScoreResult = triviaScoreResult
                ))
            elif state.getTriviaGameType() is TriviaGameType.SUPER:
                superGameState: SuperTriviaGameState = state
                await self.__triviaGameStore.removeSuperGame(superGameState.getTwitchChannel())

                self.__eventQueue.put(OutOfTimeSuperTriviaEvent(
                    triviaQuestion = superGameState.getTriviaQuestion(),
                    pointsForWinning = superGameState.getPointsForWinning(),
                    pointsMultiplier = superGameState.getPointsMultiplier(),
                    actionId = superGameState.getActionId(),
                    gameId = superGameState.getGameId(),
                    twitchChannel = superGameState.getTwitchChannel()
                ))
            else:
                raise UnknownTriviaGameTypeException(f'Unknown TriviaGameType (gameId=\"{state.getGameId()}\") (twitchChannel=\"{state.getTwitchChannel()}\"): \"{state.getTriviaGameType()}\"')

    def setEventListener(self, listener: Optional[TriviaEventListener]):
        self.__eventListener = listener

    async def __startActionLoop(self):
        while True:
            try:
                while not self.__actionQueue.empty():
                    action = self.__actionQueue.get_nowait()

                    if action.getTriviaActionType() is TriviaActionType.CHECK_ANSWER:
                        await self.__handleActionCheckAnswer(action)
                    elif action.getTriviaActionType() is TriviaActionType.CHECK_SUPER_ANSWER:
                        await self.__handleActionCheckSuperAnswer(action)
                    elif action.getTriviaActionType() is TriviaActionType.START_NEW_GAME:
                        await self.__handleActionStartNewTriviaGame(action)
                    elif action.getTriviaActionType() is TriviaActionType.START_NEW_SUPER_GAME:
                        await self.__handleActionStartNewSuperTriviaGame(action)
                    else:
                        raise UnknownTriviaActionTypeException(f'Unknown TriviaActionType: \"{action.getTriviaActionType()}\"')
            except queue.Empty as e:
                self.__timber.log('TriviaGameMachine', f'Encountered queue.Empty when looping through actions (queue size: {self.__actionQueue.qsize()}): {e}\n{repr(e)}')
            except Exception as e:
                self.__timber.log('TriviaGameMachine', f'Encountered unknown Exception when looping through actions (queue size: {self.__actionQueue.qsize()}): {e}\n{repr(e)}')

            await self.__refreshStatusOfGames()
            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __startEventLoop(self):
        while True:
            eventListener = self.__eventListener

            if eventListener is not None:
                try:
                    while not self.__eventQueue.empty():
                        event = self.__eventQueue.get_nowait()
                        await eventListener.onNewTriviaEvent(event)
                except queue.Empty as e:
                    self.__timber.log('TriviaGameMachine', f'Encountered queue.Empty when looping through events (queue size: {self.__eventQueue.qsize()}): {e}\n{repr(e)}')
                except Exception as e:
                    self.__timber.log('TriviaGameMachine', f'Encountered unknown Exception when looping through events (queue size: {self.__eventQueue.qsize()}): {e}\n{repr(e)}')

            await asyncio.sleep(self.__sleepTimeSeconds)

    def submitAction(self, action: AbsTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        self.__actionQueue.put(action)
