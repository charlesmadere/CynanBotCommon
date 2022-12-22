import asyncio
import queue
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from queue import SimpleQueue
from typing import Any, Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cuteness.cutenessRepository import CutenessRepository
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.absTriviaGameState import AbsTriviaGameState
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.checkAnswerTriviaAction import \
        CheckAnswerTriviaAction
    from CynanBotCommon.trivia.checkSuperAnswerTriviaAction import \
        CheckSuperAnswerTriviaAction
    from CynanBotCommon.trivia.clearedSuperTriviaQueueTriviaEvent import \
        ClearedSuperTriviaQueueTriviaEvent
    from CynanBotCommon.trivia.clearSuperTriviaQueueTriviaAction import \
        ClearSuperTriviaQueueTriviaAction
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
    from CynanBotCommon.trivia.shinyTriviaHelper import ShinyTriviaHelper
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.startNewTriviaGameAction import \
        StartNewTriviaGameAction
    from CynanBotCommon.trivia.superGameNotReadyCheckAnswerTriviaEvent import \
        SuperGameNotReadyCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.superTriviaCooldownHelper import \
        SuperTriviaCooldownHelper
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
    from cuteness.cutenessRepository import CutenessRepository
    from timber.timber import Timber
    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.absTriviaGameState import AbsTriviaGameState
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.checkAnswerTriviaAction import CheckAnswerTriviaAction
    from trivia.checkSuperAnswerTriviaAction import \
        CheckSuperAnswerTriviaAction
    from trivia.clearedSuperTriviaQueueTriviaEvent import \
        ClearedSuperTriviaQueueTriviaEvent
    from trivia.clearSuperTriviaQueueTriviaAction import \
        ClearSuperTriviaQueueTriviaAction
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
    from trivia.shinyTriviaHelper import ShinyTriviaHelper
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.startNewTriviaGameAction import StartNewTriviaGameAction
    from trivia.superGameNotReadyCheckAnswerTriviaEvent import \
        SuperGameNotReadyCheckAnswerTriviaEvent
    from trivia.superTriviaCooldownHelper import SuperTriviaCooldownHelper
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
        cutenessRepository: CutenessRepository,
        queuedTriviaGameStore: QueuedTriviaGameStore,
        shinyTriviaHelper: ShinyTriviaHelper,
        superTriviaCooldownHelper: SuperTriviaCooldownHelper,
        timber: Timber,
        triviaAnswerChecker: TriviaAnswerChecker,
        triviaGameStore: TriviaGameStore,
        triviaRepository: TriviaRepository,
        triviaScoreRepository: TriviaScoreRepository,
        sleepTimeSeconds: float = 0.5,
        queueTimeoutSeconds: int = 3,
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(eventLoop, AbstractEventLoop):
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif not isinstance(cutenessRepository, CutenessRepository):
            raise ValueError(f'cutenessRepository argument is malformed: \"{cutenessRepository}\"')
        elif not isinstance(queuedTriviaGameStore, QueuedTriviaGameStore):
            raise ValueError(f'queuedTriviaGameStore argument is malformed: \"{queuedTriviaGameStore}\"')
        elif not isinstance(shinyTriviaHelper, ShinyTriviaHelper):
            raise ValueError(f'shinyTriviaHelper argument is malformed: \"{shinyTriviaHelper}\"')
        elif not isinstance(superTriviaCooldownHelper, SuperTriviaCooldownHelper):
            raise ValueError(f'superTriviaCooldownHelper argument is malformed: \"{superTriviaCooldownHelper}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaAnswerChecker, TriviaAnswerChecker):
            raise ValueError(f'triviaAnswerChecker argument is malformed: \"{triviaAnswerChecker}\"')
        elif not isinstance(triviaGameStore, TriviaGameStore):
            raise ValueError(f'triviaGameStore argument is malformed: \"{triviaGameStore}\"')
        elif not isinstance(triviaRepository, TriviaRepository):
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')
        elif not isinstance(triviaScoreRepository, TriviaScoreRepository):
            raise ValueError(f'triviaScoreRepository argument is malformed: \"{triviaScoreRepository}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 0.25 or sleepTimeSeconds > 3:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__cutenessRepository: CutenessRepository = cutenessRepository
        self.__queuedTriviaGameStore: QueuedTriviaGameStore = queuedTriviaGameStore
        self.__shinyTriviaHelper: ShinyTriviaHelper = shinyTriviaHelper
        self.__superTriviaCooldownHelper: SuperTriviaCooldownHelper = superTriviaCooldownHelper
        self.__timber: Timber = timber
        self.__triviaAnswerChecker: TriviaAnswerChecker = triviaAnswerChecker
        self.__triviaGameStore: TriviaGameStore = triviaGameStore
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaScoreRepository: TriviaScoreRepository = triviaScoreRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__timeZone: timezone = timeZone

        self.__eventListener: Optional[TriviaEventListener] = None
        self.__actionQueue: SimpleQueue[AbsTriviaAction] = SimpleQueue()
        self.__eventQueue: SimpleQueue[AbsTriviaEvent] = SimpleQueue()
        eventLoop.create_task(self.__startActionLoop())
        eventLoop.create_task(self.__startEventLoop())

    async def __beginQueuedTriviaGames(self):
        activeChannelsSet: Set[str] = set()
        activeChannelsSet.update(await self.__triviaGameStore.getTwitchChannelsWithActiveSuperGames())
        activeChannelsSet.update(await self.__superTriviaCooldownHelper.getTwitchChannelsInCooldown())

        activeChannelsList: List[str] = list(activeChannelsSet)
        queuedSuperGames = await self.__queuedTriviaGameStore.popQueuedSuperGames(activeChannelsList)

        for queuedSuperGame in queuedSuperGames:
            remainingQueueSize = await self.__queuedTriviaGameStore.getQueuedSuperGamesSize(
                twitchChannel = queuedSuperGame.getTwitchChannel()
            )

            self.__timber.log('TriviaGameMachine', f'Starting new queued super trivia game for \"{queuedSuperGame.getTwitchChannel()}\", with {remainingQueueSize} game(s) remaining in their queue (actionId=\"{queuedSuperGame.getActionId()}\")')
            await self.__handleActionStartNewSuperTriviaGame(queuedSuperGame)

    async def __checkAnswer(
        self,
        answer: Optional[str],
        triviaQuestion: AbsTriviaQuestion,
        extras: Optional[Dict[str, Any]] = None
    ) -> TriviaAnswerCheckResult:
        if not isinstance(triviaQuestion, AbsTriviaQuestion):
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        return await self.__triviaAnswerChecker.checkAnswer(answer, triviaQuestion, extras)

    async def __handleActionCheckAnswer(self, action: CheckAnswerTriviaAction):
        if not isinstance(action, CheckAnswerTriviaAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = await self.__triviaGameStore.getNormalGame(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        now = datetime.now(self.__timeZone)

        if state is None:
            await self.__submitEvent(GameNotReadyCheckAnswerTriviaEvent(
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getUserId() != action.getUserId():
            await self.__submitEvent(WrongUserCheckAnswerTriviaEvent(
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
            await self.__removeNormalTriviaGame(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

            triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaLosses(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

            await self.__submitEvent(TooLateToAnswerCheckAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                isShiny = state.isShiny(),
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
            await self.__submitEvent(InvalidAnswerInputTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                isShiny = state.isShiny(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        await self.__removeNormalTriviaGame(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        if checkResult is TriviaAnswerCheckResult.INCORRECT:
            triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaLosses(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

            await self.__submitEvent(IncorrectAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                isShiny = state.isShiny(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName(),
                triviaScoreResult = triviaScoreResult
            ))
            return

        pointsForWinning = state.getPointsForWinning()
        if state.isShiny():
            pointsForWinning = pointsForWinning * state.getShinyTriviaMultiplier()

        cutenessResult = await self.__cutenessRepository.fetchCutenessIncrementedBy(
            incrementAmount = pointsForWinning,
            twitchChannel = state.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        )

        triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaWins(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        await self.__submitEvent(CorrectAnswerTriviaEvent(
            triviaQuestion = state.getTriviaQuestion(),
            isShiny = state.isShiny(),
            cutenessResult = cutenessResult,
            pointsForWinning = pointsForWinning,
            actionId = action.getActionId(),
            answer = action.getAnswer(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName(),
            triviaScoreResult = triviaScoreResult
        ))

    async def __handleActionCheckSuperAnswer(self, action: CheckSuperAnswerTriviaAction):
        if not isinstance(action, CheckSuperAnswerTriviaAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_SUPER_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_SUPER_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = await self.__triviaGameStore.getSuperGame(action.getTwitchChannel())
        now = datetime.now(self.__timeZone)

        if state is None:
            await self.__submitEvent(SuperGameNotReadyCheckAnswerTriviaEvent(
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getEndTime() < now:
            await self.__submitEvent(TooLateToAnswerCheckSuperAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                isShiny = state.isShiny(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if not state.isEligibleToAnswer(action.getUserId()):
            return

        state.incrementAnswerCount(action.getUserId())

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
            await self.__submitEvent(IncorrectSuperAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                isShiny = state.isShiny(),
                actionId = action.getActionId(),
                answer = action.getAnswer(),
                gameId = state.getGameId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        await self.__removeSuperTriviaGame(action.getTwitchChannel())

        pointsForWinning = state.getPointsForWinning()
        if state.isShiny():
            pointsForWinning = pointsForWinning * state.getShinyTriviaMultiplier()
        else:
            pointsForWinning = pointsForWinning * state.getPointsMultiplier()

        cutenessResult = await self.__cutenessRepository.fetchCutenessIncrementedBy(
            incrementAmount = pointsForWinning,
            twitchChannel = state.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        )

        remainingQueueSize = await self.__queuedTriviaGameStore.getQueuedSuperGamesSize(
            twitchChannel = action.getTwitchChannel()
        )

        triviaScoreResult = await self.__triviaScoreRepository.incrementSuperTriviaWins(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        await self.__submitEvent(CorrectSuperAnswerTriviaEvent(
            triviaQuestion = state.getTriviaQuestion(),
            isShiny = state.isShiny(),
            cutenessResult = cutenessResult,
            pointsForWinning = pointsForWinning,
            remainingQueueSize = remainingQueueSize,
            actionId = action.getActionId(),
            answer = action.getAnswer(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName(),
            triviaScoreResult = triviaScoreResult
        ))

    async def __handleActionClearSuperTriviaQueue(self, action: ClearSuperTriviaQueueTriviaAction):
        if not isinstance(action, ClearSuperTriviaQueueTriviaAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CLEAR_SUPER_TRIVIA_QUEUE:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CLEAR_SUPER_TRIVIA_QUEUE}: \"{action.getTriviaActionType()}\"')

        result = await self.__queuedTriviaGameStore.clearQueuedSuperGames(
            twitchChannel = action.getTwitchChannel()
        )

        self.__timber.log('TriviaGameMachine', f'Cleared Super Trivia game queue for \"{action.getTwitchChannel()}\" (actionId=\"{action.getActionId()}\"): {result.toStr()}')

        await self.__submitEvent(ClearedSuperTriviaQueueTriviaEvent(
            numberOfGamesRemoved = result.getAmountRemoved(),
            previousQueueSize = result.getOldQueueSize(),
            actionId = action.getActionId(),
            twitchChannel = action.getTwitchChannel()
        ))

    async def __handleActionStartNewTriviaGame(self, action: StartNewTriviaGameAction):
        if not isinstance(action, StartNewTriviaGameAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_GAME}: \"{action.getTriviaActionType()}\"')

        now = datetime.now(self.__timeZone)
        state = await self.__triviaGameStore.getNormalGame(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        if state is not None and state.getEndTime() >= now:
            await self.__submitEvent(GameAlreadyInProgressTriviaEvent(
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
            self.__timber.log('TriviaGameMachine', f'Reached limit on trivia fetch attempts without being able to successfully retrieve a trivia question for \"{action.getTwitchChannel()}\": {e}', e)

        if triviaQuestion is None:
            await self.__submitEvent(FailedToFetchQuestionTriviaEvent(
                actionId = action.getActionId(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        isShiny = False
        if action.isShinyTriviaEnabled():
            isShiny = await self.__shinyTriviaHelper.isShinyTriviaQuestion(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

        state = TriviaGameState(
            triviaQuestion = triviaQuestion,
            isShiny = isShiny,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            shinyTriviaMultiplier = action.getShinyTriviaMultiplier(),
            actionId = action.getActionId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        )

        await self.__triviaGameStore.add(state)

        await self.__submitEvent(NewTriviaGameEvent(
            triviaQuestion = triviaQuestion,
            isShiny = isShiny,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            shinyTriviaMultiplier = action.getShinyTriviaMultiplier(),
            actionId = action.getActionId(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        ))

    async def __handleActionStartNewSuperTriviaGame(self, action: StartNewSuperTriviaGameAction):
        if not isinstance(action, StartNewSuperTriviaGameAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_SUPER_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_SUPER_GAME}: \"{action.getTriviaActionType()}\"')

        now = datetime.now(self.__timeZone)
        state = await self.__triviaGameStore.getSuperGame(action.getTwitchChannel())
        isSuperTriviaGameCurrentlyInProgress = state is not None and state.getEndTime() >= now

        queueResult = await self.__queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = isSuperTriviaGameCurrentlyInProgress,
            action = action
        )

        if queueResult.getAmountAdded() >= 1:
            self.__timber.log('TriviaGameMachine', f'Queued new Super Trivia game(s) for \"{action.getTwitchChannel()}\" (actionId=\"{action.getActionId()}\"): {queueResult.toStr()}')

            await self.__submitEvent(NewQueuedSuperTriviaGameEvent(
                numberOfGames = queueResult.getAmountAdded(),
                pointsForWinning = action.getPointsForWinning(),
                pointsMultiplier = action.getPointsMultiplier(),
                secondsToLive = action.getSecondsToLive(),
                actionId = action.getActionId(),
                twitchChannel = action.getTwitchChannel()
            ))

        if isSuperTriviaGameCurrentlyInProgress:
            return
        elif not self.__superTriviaCooldownHelper[action.getTwitchChannel()]:
            # re-add this action back into the queue to try processing again later, as we are on cooldown
            self.submitAction(action)
            return

        triviaQuestion: Optional[AbsTriviaQuestion] = None
        try:
            triviaQuestion = await self.__triviaRepository.fetchTrivia(action.getTriviaFetchOptions())
        except TooManyTriviaFetchAttemptsException as e:
            self.__timber.log('TriviaGameMachine', f'Reached limit on trivia fetch attempts without being able to successfully retrieve a super trivia question for \"{action.getTwitchChannel()}\": {e}', e)

        if triviaQuestion is None:
            await self.__submitEvent(FailedToFetchQuestionSuperTriviaEvent(
                actionId = action.getActionId(),
                twitchChannel = action.getTwitchChannel()
            ))
            return

        isShiny = False
        if action.isShinyTriviaEnabled():
            isShiny = await self.__shinyTriviaHelper.isShinySuperTriviaQuestion(
                twitchChannel = action.getTwitchChannel()
            )

        state = SuperTriviaGameState(
            triviaQuestion = triviaQuestion,
            isShiny = isShiny,
            perUserAttempts = action.getPerUserAttempts(),
            pointsForWinning = action.getPointsForWinning(),
            pointsMultiplier = action.getPointsMultiplier(),
            secondsToLive = action.getSecondsToLive(),
            shinyTriviaMultiplier = action.getShinyTriviaMultiplier(),
            actionId = action.getActionId(),
            twitchChannel = action.getTwitchChannel()
        )

        await self.__triviaGameStore.add(state)

        await self.__submitEvent(NewSuperTriviaGameEvent(
            triviaQuestion = triviaQuestion,
            isShiny = isShiny,
            pointsForWinning = action.getPointsForWinning(),
            pointsMultiplier = action.getPointsMultiplier(),
            secondsToLive = action.getSecondsToLive(),
            shinyTriviaMultiplier = action.getShinyTriviaMultiplier(),
            actionId = action.getActionId(),
            gameId = state.getGameId(),
            twitchChannel = action.getTwitchChannel(),
        ))

    async def __refreshStatusOfTriviaGames(self):
        await self.__removeDeadTriviaGames()
        await self.__beginQueuedTriviaGames()

    async def __removeDeadTriviaGames(self):
        now = datetime.now(self.__timeZone)
        gameStates = await self.__triviaGameStore.getAll()
        gameStatesToRemove: List[AbsTriviaGameState] = list()

        for state in gameStates:
            if state.getEndTime() < now:
                gameStatesToRemove.append(state)

        for state in gameStatesToRemove:
            if state.getTriviaGameType() is TriviaGameType.NORMAL:
                normalGameState: TriviaGameState = state

                await self.__removeNormalTriviaGame(
                    twitchChannel = normalGameState.getTwitchChannel(),
                    userId = normalGameState.getUserId()
                )

                triviaScoreResult = await self.__triviaScoreRepository.incrementTriviaLosses(
                    twitchChannel = normalGameState.getTwitchChannel(),
                    userId = normalGameState.getUserId()
                )

                await self.__submitEvent(OutOfTimeTriviaEvent(
                    triviaQuestion = normalGameState.getTriviaQuestion(),
                    isShiny = normalGameState.isShiny(),
                    pointsForWinning = normalGameState.getPointsForWinning(),
                    actionId = normalGameState.getActionId(),
                    gameId = normalGameState.getGameId(),
                    twitchChannel = normalGameState.getTwitchChannel(),
                    userId = normalGameState.getUserId(),
                    userName = normalGameState.getUserName(),
                    triviaScoreResult = triviaScoreResult
                ))
            elif state.getTriviaGameType() is TriviaGameType.SUPER:
                superGameState: SuperTriviaGameState = state
                await self.__removeSuperTriviaGame(superGameState.getTwitchChannel())

                remainingQueueSize = await self.__queuedTriviaGameStore.getQueuedSuperGamesSize(
                    twitchChannel = superGameState.getTwitchChannel()
                )

                await self.__submitEvent(OutOfTimeSuperTriviaEvent(
                    triviaQuestion = superGameState.getTriviaQuestion(),
                    isShiny = superGameState.isShiny(),
                    pointsForWinning = superGameState.getPointsForWinning(),
                    pointsMultiplier = superGameState.getPointsMultiplier(),
                    remainingQueueSize = remainingQueueSize,
                    actionId = superGameState.getActionId(),
                    gameId = superGameState.getGameId(),
                    twitchChannel = superGameState.getTwitchChannel()
                ))
            else:
                raise UnknownTriviaGameTypeException(f'Unknown TriviaGameType (gameId=\"{state.getGameId()}\") (twitchChannel=\"{state.getTwitchChannel()}\") (actionId=\"{state.getActionId()}\"): \"{state.getTriviaGameType()}\"')

    async def __removeNormalTriviaGame(self, twitchChannel: str, userId: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        await self.__triviaGameStore.removeNormalGame(
            twitchChannel = twitchChannel,
            userId = userId
        )

    async def __removeSuperTriviaGame(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        await self.__triviaGameStore.removeSuperGame(twitchChannel)
        await self.__superTriviaCooldownHelper.update(twitchChannel)

    def setEventListener(self, listener: Optional[TriviaEventListener]):
        self.__eventListener = listener

    async def __startActionLoop(self):
        while True:
            actions: List[AbsTriviaAction] = list()

            try:
                while not self.__actionQueue.empty():
                    actions.append(self.__actionQueue.get_nowait())
            except queue.Empty as e:
                self.__timber.log('TriviaGameMachine', f'Encountered queue.Empty when building up actions list (queue size: {self.__actionQueue.qsize()}) (actions size: {len(actions)}): {e}', e)

            try:
                for action in actions:
                    triviaActionType = action.getTriviaActionType()

                    if triviaActionType is TriviaActionType.CHECK_ANSWER:
                        await self.__handleActionCheckAnswer(action)
                    elif triviaActionType is TriviaActionType.CHECK_SUPER_ANSWER:
                        await self.__handleActionCheckSuperAnswer(action)
                    elif triviaActionType is TriviaActionType.CLEAR_SUPER_TRIVIA_QUEUE:
                        await self.__handleActionClearSuperTriviaQueue(action)
                    elif triviaActionType is TriviaActionType.START_NEW_GAME:
                        await self.__handleActionStartNewTriviaGame(action)
                    elif triviaActionType is TriviaActionType.START_NEW_SUPER_GAME:
                        await self.__handleActionStartNewSuperTriviaGame(action)
                    else:
                        raise UnknownTriviaActionTypeException(f'Unknown TriviaActionType: \"{action.getTriviaActionType()}\"')
            except Exception as e:
                self.__timber.log('TriviaGameMachine', f'Encountered unknown Exception when looping through actions (queue size: {self.__actionQueue.qsize()}) (actions size: {len(actions)}): {e}', e)

            try:
                await self.__refreshStatusOfTriviaGames()
            except Exception as e:
                self.__timber.log('TriviaGameMachine', f'Encountered unknown Exception when refreshing status of trivia games: {e}', e)

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __startEventLoop(self):
        while True:
            eventListener = self.__eventListener

            if eventListener is not None:
                events: List[AbsTriviaEvent] = list()

                try:
                    while not self.__eventQueue.empty():
                        events.append(self.__eventQueue.get_nowait())
                except queue.Empty as e:
                    self.__timber.log('TriviaGameMachine', f'Encountered queue.Empty when building up events list (queue size: {self.__eventQueue.qsize()}) (events size: {len(events)}): {e}', e)

                for event in events:
                    try:
                        await eventListener.onNewTriviaEvent(event)
                    except Exception as e:
                        self.__timber.log('TriviaGameMachine', f'Encountered unknown Exception when looping through events (queue size: {self.__eventQueue.qsize()}) (event: {event}): {e}', e)

            await asyncio.sleep(self.__sleepTimeSeconds)

    def submitAction(self, action: AbsTriviaAction):
        if not isinstance(action, AbsTriviaAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        try:
            self.__actionQueue.put(action, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('TriviaGameMachine', f'Encountered queue.Full when submitting a new action ({action}) into the action queue (queue size: {self.__actionQueue.qsize()}): {e}', e)

    async def __submitEvent(self, event: AbsTriviaEvent):
        if not isinstance(event, AbsTriviaEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        try:
            self.__eventQueue.put(event, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('TriviaGameMachine', f'Encountered queue.Full when submitting a new event ({event}) into the event queue (queue size: {self.__eventQueue.qsize()}): {e}', e)
