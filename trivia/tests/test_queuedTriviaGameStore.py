import asyncio
from asyncio import AbstractEventLoop

import pytest

try:
    from ...timber.timber import Timber
    from ...trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
    from ...trivia.queuedTriviaGameStore import QueuedTriviaGameStore
    from ...trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from ...trivia.triviaFetchOptions import TriviaFetchOptions
    from ...trivia.triviaSettingsRepository import TriviaSettingsRepository
except:
    from timber.timber import Timber
    from trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
    from trivia.queuedTriviaGameStore import QueuedTriviaGameStore
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class TestQueuedTriviaGameStore():

    eventLoop: AbstractEventLoop = asyncio.get_event_loop()
    timber = Timber(
        eventLoop = eventLoop
    )
    triviaSettingsRepository = TriviaSettingsRepository()
    queuedTriviaGameStore = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    startNewSuperTriviaGameAction1 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        numberOfGames = 3,
        perUserAttempts = 2,
        pointsForWinning = 5,
        pointsMultiplier = 5,
        secondsToLive = 50,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    startNewSuperTriviaGameAction2 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        numberOfGames = 1,
        perUserAttempts = 2,
        pointsForWinning = 5,
        pointsMultiplier = 5,
        secondsToLive = 50,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    startNewSuperTriviaGameAction3 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = True,
        numberOfGames = 1,
        perUserAttempts = 2,
        pointsForWinning = 5,
        pointsMultiplier = 5,
        secondsToLive = 50,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    startNewSuperTriviaGameAction4 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        numberOfGames = 5,
        perUserAttempts = 2,
        pointsForWinning = 5,
        pointsMultiplier = 5,
        secondsToLive = 50,
        twitchChannel = 'stashiocat',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'stashiocat',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    @pytest.mark.asyncio
    async def test_addQueuedSuperGamesSize_withEmptyTwitchChannel_andSuperGameIsNotInProgress(self):
        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = False,
            action = self.startNewSuperTriviaGameAction1
        )
        assert result.getAmountAdded() == 2
        assert result.getNewQueueSize() == 2
        assert result.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction1.isQueueActionConsumed() is True

        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction1
        )
        assert result.getAmountAdded() == 0
        assert result.getNewQueueSize() == 2
        assert result.getOldQueueSize() == 2
        assert self.startNewSuperTriviaGameAction1.isQueueActionConsumed() is True

        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction2
        )
        assert result.getAmountAdded() == 1
        assert result.getNewQueueSize() == 3
        assert result.getOldQueueSize() == 2
        assert self.startNewSuperTriviaGameAction2.isQueueActionConsumed() is True

        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction3
        )
        assert result.getAmountAdded() == 0
        assert result.getNewQueueSize() == 3
        assert result.getOldQueueSize() == 3
        assert self.startNewSuperTriviaGameAction3.isQueueActionConsumed() is True

        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = False,
            action = self.startNewSuperTriviaGameAction4
        )
        assert result.getAmountAdded() == 4
        assert result.getNewQueueSize() == 7
        assert result.getOldQueueSize() == 3
        assert self.startNewSuperTriviaGameAction4.isQueueActionConsumed() is True

    @pytest.mark.asyncio
    async def test_addQueuedSuperGamesSize_withEmptyTwitchChannel_andSuperGameIsInProgress(self):
        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction4
        )

        assert result.getAmountAdded() == 5
        assert result.getNewQueueSize() == 5
        assert result.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction4.isQueueActionConsumed() is True

    @pytest.mark.asyncio
    async def test_clearQueuedSuperGames(self):
        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames(
            twitchChannel = self.startNewSuperTriviaGameAction1.getTwitchChannel()
        )
        assert clearResult.getAmountRemoved() == 0
        assert clearResult.getOldQueueSize() == 0

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = False,
            action = self.startNewSuperTriviaGameAction1
        )
        assert addResult.getAmountAdded() == 2
        assert addResult.getNewQueueSize() == 2
        assert addResult.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction1.isQueueActionConsumed()

        queueSize = await self.queuedTriviaGameStore.getQueuedSuperGamesSize(
            twitchChannel = self.startNewSuperTriviaGameAction1.getTwitchChannel()
        )
        assert queueSize == 2

        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames(
            twitchChannel = self.startNewSuperTriviaGameAction1.getTwitchChannel()
        )
        assert clearResult.getAmountRemoved() == 2
        assert clearResult.getOldQueueSize() == 2

        queueSize = await self.queuedTriviaGameStore.getQueuedSuperGamesSize(
            twitchChannel = self.startNewSuperTriviaGameAction1.getTwitchChannel()
        )
        assert queueSize == 0

    @pytest.mark.asyncio
    async def test_clearQueuedSuperGames_withEmptyTwitchChannel(self):
        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames('imyt')
        assert clearResult.getAmountRemoved() == 0
        assert clearResult.getOldQueueSize() == 0

    @pytest.mark.asyncio
    async def test_getQueuedSuperGamesSize_withEmptyTwitchChannel(self):
        size = await self.queuedTriviaGameStore.getQueuedSuperGamesSize('Oatsngoats')
        assert size == 0
