import asyncio
import queue
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from queue import SimpleQueue
from typing import List

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
    from CynanBotCommon.trivia.newSuperTriviaGameEvent import \
        NewSuperTriviaGameEvent
    from CynanBotCommon.trivia.newTriviaGameEvent import NewTriviaGameEvent
    from CynanBotCommon.trivia.outOfTimeCheckAnswerTriviaEvent import \
        OutOfTimeCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.outOfTimeCheckSuperAnswerTriviaEvent import \
        OutOfTimeCheckSuperAnswerTriviaEvent
    from CynanBotCommon.trivia.outOfTimeSuperTriviaEvent import \
        OutOfTimeSuperTriviaEvent
    from CynanBotCommon.trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.startNewTriviaGameAction import \
        StartNewTriviaGameAction
    from CynanBotCommon.trivia.superGameAlreadyInProgressTriviaEvent import \
        SuperGameAlreadyInProgressTriviaEvent
    from CynanBotCommon.trivia.superGameNotReadyCheckAnswerTriviaEvent import \
        SuperGameNotReadyCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.superTriviaGameState import SuperTriviaGameState
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
    from CynanBotCommon.trivia.triviaAnswerChecker import TriviaAnswerChecker
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
    from trivia.newSuperTriviaGameEvent import NewSuperTriviaGameEvent
    from trivia.newTriviaGameEvent import NewTriviaGameEvent
    from trivia.outOfTimeCheckAnswerTriviaEvent import \
        OutOfTimeCheckAnswerTriviaEvent
    from trivia.outOfTimeCheckSuperAnswerTriviaEvent import \
        OutOfTimeCheckSuperAnswerTriviaEvent
    from trivia.outOfTimeSuperTriviaEvent import OutOfTimeSuperTriviaEvent
    from trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.startNewTriviaGameAction import StartNewTriviaGameAction
    from trivia.superGameAlreadyInProgressTriviaEvent import \
        SuperGameAlreadyInProgressTriviaEvent
    from trivia.superGameNotReadyCheckAnswerTriviaEvent import \
        SuperGameNotReadyCheckAnswerTriviaEvent
    from trivia.superTriviaGameState import SuperTriviaGameState
    from trivia.triviaActionType import TriviaActionType
    from trivia.triviaAnswerChecker import TriviaAnswerChecker
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
        timber: Timber,
        triviaAnswerChecker: TriviaAnswerChecker,
        triviaGameStore: TriviaGameStore,
        triviaRepository: TriviaRepository,
        triviaScoreRepository: TriviaScoreRepository,
        sleepTimeSeconds: float = 0.5
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
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
        elif sleepTimeSeconds < 0.1 or sleepTimeSeconds > 5:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')

        self.__timber: Timber = timber
        self.__triviaAnswerChecker: TriviaAnswerChecker = triviaAnswerChecker
        self.__triviaGameStore: TriviaGameStore = triviaGameStore
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaScoreRepository: TriviaScoreRepository = triviaScoreRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds

        self.__eventListener = None
        self.__actionQueue: SimpleQueue[AbsTriviaAction] = SimpleQueue()
        self.__eventQueue: SimpleQueue[AbsTriviaEvent] = SimpleQueue()
        eventLoop.create_task(self.__startActionLoop())
        eventLoop.create_task(self.__startEventLoop())

    async def __checkAnswer(self, answer: str, triviaQuestion: AbsTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        return await self.__triviaAnswerChecker.checkAnswer(answer, triviaQuestion)

    async def __handleActionCheckAnswer(self, action: CheckAnswerTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = await self.__triviaGameStore.getNormalGame(action.getTwitchChannel())
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
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getEndTime() < now:
            self.__eventQueue.put(OutOfTimeCheckAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        await self.__triviaGameStore.removeNormalGame(action.getTwitchChannel())

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

    async def __handleActionCheckSuperAnswer(self, action: CheckAnswerTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_SUPER_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_SUPER_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = await self.__triviaGameStore.getSuperGame(action.getTwitchChannel())
        now = datetime.now(timezone.utc)

        if state is None:
            self.__eventQueue.put(SuperGameNotReadyCheckAnswerTriviaEvent(
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getEndTime() < now:
            self.__eventQueue.put(OutOfTimeCheckSuperAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.hasAnswered(action.getUserName()):
            return

        state.setHasAnswered(action.getUserName())

        if not await self.__checkAnswer(action.getAnswer(), state.getTriviaQuestion()):
            self.__eventQueue.put(IncorrectSuperAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        await self.__triviaGameStore.removeSuperGame(action.getTwitchChannel())

        triviaScoreResult = await self.__triviaScoreRepository.incrementTotalWins(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        self.__eventQueue.put(CorrectSuperAnswerTriviaEvent(
            triviaQuestion = state.getTriviaQuestion(),
            pointsForWinning = state.getPointsForWinning(),
            pointsMultiplier = state.getPointsMultiplier(),
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

        state = await self.__triviaGameStore.getNormalGame(action.getTwitchChannel())
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
            triviaQuestion = await self.__triviaRepository.fetchTrivia(action.getTriviaFetchOptions())
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

        await self.__triviaGameStore.add(state)

        self.__eventQueue.put(NewTriviaGameEvent(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
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

        state = await self.__triviaGameStore.getSuperGame(action.getTwitchChannel())
        now = datetime.now(timezone.utc)

        if state is not None and state.getEndTime() < now:
            self.__eventQueue.put(SuperGameAlreadyInProgressTriviaEvent(
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel()
            ))
            return

        triviaQuestion: AbsTriviaQuestion = None
        try:
            triviaQuestion = await self.__triviaRepository.fetchTrivia(action.getTriviaFetchOptions())
        except TooManyTriviaFetchAttemptsException as e:
            self.__timber.log('TriviaGameMachine', f'Reached limit on trivia fetch attempts without being able to successfully retrieve a question: {e}')

        if triviaQuestion is None:
            self.__eventQueue.put(FailedToFetchQuestionSuperTriviaEvent(
                twitchChannel = action.getTwitchChannel()
            ))
            return

        state = SuperTriviaGameState(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            pointsMultiplier = action.getPointsMultiplier(),
            secondsToLive = action.getSecondsToLive(),
            twitchChannel = action.getTwitchChannel()
        )

        await self.__triviaGameStore.add(state)

        self.__eventQueue.put(NewSuperTriviaGameEvent(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            pointsMultiplier = action.getPointsMultiplier(),
            secondsToLive = action.getSecondsToLive(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
        ))

    async def __refreshStatusOfGames(self):
        gameStates = await self.__triviaGameStore.getAll()

        if not utils.hasItems(gameStates):
            return

        now = datetime.now(timezone.utc)
        gameStatesToRemove: List[AbsTriviaGameState] = list()

        for state in gameStates:
            if state.getEndTime() < now:
                gameStatesToRemove.append(state)

        if not utils.hasItems(gameStatesToRemove):
            return

        for state in gameStatesToRemove:
            if state.getTriviaGameType() is TriviaGameType.NORMAL:
                normalGameState: TriviaGameState = state
                await self.__triviaGameStore.removeNormalGame(state.getTwitchChannel())

                triviaScoreResult = await self.__triviaScoreRepository.incrementTotalLosses(
                    twitchChannel = normalGameState.getTwitchChannel(),
                    userId = normalGameState.getUserId()
                )

                self.__eventQueue.put(OutOfTimeTriviaEvent(
                    triviaQuestion = normalGameState.getTriviaQuestion(),
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
                    gameId = superGameState.getGameId(),
                    twitchChannel = superGameState.getTwitchChannel()
                ))
            else:
                raise UnknownTriviaGameTypeException(f'Unknown TriviaGameType: \"{state.getTriviaGameType()}\"')

    def setEventListener(self, listener):
        self.__eventListener = listener

    async def __startActionLoop(self):
        while True:
            try:
                while not self.__actionQueue.empty():
                    action = self.__actionQueue.get(block = False)

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
                self.__timber.log('TriviaGameMachine', f'Encountered queue.Empty error when looping through actions (queue size: {self.__actionQueue.qsize()}): {e}')

            await self.__refreshStatusOfGames()
            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __startEventLoop(self):
        while True:
            eventListener = self.__eventListener

            if eventListener is not None:
                try:
                    while not self.__eventQueue.empty():
                        event = self.__eventQueue.get(block = False)
                        await eventListener(event)
                except queue.Empty as e:
                    self.__timber.log('TriviaGameMachine', f'Encountered queue.Empty error when looping through events (queue size: {self.__eventQueue.qsize()}): {e}')

            await asyncio.sleep(self.__sleepTimeSeconds)

    def submitAction(self, action: AbsTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        self.__actionQueue.put(action)
