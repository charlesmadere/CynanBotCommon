import pytest

try:
    from ...storage.jsonStaticReader import JsonStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ..questionAnswerTriviaConditions import QuestionAnswerTriviaConditions
    from ..queuedTriviaGameStore import QueuedTriviaGameStore
    from ..queuedTriviaGameStoreInterface import QueuedTriviaGameStoreInterface
    from ..startNewSuperTriviaGameAction import StartNewSuperTriviaGameAction
    from ..triviaFetchOptions import TriviaFetchOptions
    from ..triviaSettingsRepository import TriviaSettingsRepository
    from ..triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
except:
    from storage.jsonStaticReader import JsonStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub
    from trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
    from trivia.queuedTriviaGameStore import QueuedTriviaGameStore
    from trivia.queuedTriviaGameStoreInterface import \
        QueuedTriviaGameStoreInterface
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface


class TestQueuedTriviaGameStore1():

    timber: TimberInterface = TimberStub()

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    queuedTriviaGameStore: QueuedTriviaGameStoreInterface = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    startNewSuperTriviaGameAction1 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 3,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    startNewSuperTriviaGameAction2 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 1,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    startNewSuperTriviaGameAction3 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = True,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 1,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    startNewSuperTriviaGameAction4 = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 5,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'stashiocat',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'stashiocat',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    @pytest.mark.asyncio
    async def test_addQueuedSuperGamesSize_withEmptyTwitchChannel_andSuperGameIsNotInProgress(self):
        assert self.startNewSuperTriviaGameAction1.isQueueActionConsumed() is False

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = False,
            action = self.startNewSuperTriviaGameAction1
        )
        assert addResult.getAmountAdded() == 2
        assert addResult.getNewQueueSize() == 2
        assert addResult.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction1.isQueueActionConsumed() is True

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction1
        )
        assert addResult.getAmountAdded() == 0
        assert addResult.getNewQueueSize() == 2
        assert addResult.getOldQueueSize() == 2
        assert self.startNewSuperTriviaGameAction1.isQueueActionConsumed() is True

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction2
        )
        assert addResult.getAmountAdded() == 1
        assert addResult.getNewQueueSize() == 3
        assert addResult.getOldQueueSize() == 2
        assert self.startNewSuperTriviaGameAction2.isQueueActionConsumed() is True

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction3
        )
        assert addResult.getAmountAdded() == 0
        assert addResult.getNewQueueSize() == 3
        assert addResult.getOldQueueSize() == 3
        assert self.startNewSuperTriviaGameAction3.isQueueActionConsumed() is True

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = False,
            action = self.startNewSuperTriviaGameAction4
        )
        assert addResult.getAmountAdded() == 4
        assert addResult.getNewQueueSize() == 4
        assert addResult.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction4.isQueueActionConsumed() is True

    def test_sanity(self):
        assert self.queuedTriviaGameStore is not None
        assert isinstance(self.queuedTriviaGameStore, QueuedTriviaGameStoreInterface)


class TestQueuedTriviaGameStore2():

    timber: TimberInterface = TimberStub()

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    queuedTriviaGameStore: QueuedTriviaGameStoreInterface = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_getQueuedSuperGamesSize_withEmptyTwitchChannel(self):
        size = await self.queuedTriviaGameStore.getQueuedSuperGamesSize('Oatsngoats')
        assert size == 0

    def test_sanity(self):
        assert self.queuedTriviaGameStore is not None
        assert isinstance(self.queuedTriviaGameStore, QueuedTriviaGameStoreInterface)


class TestQueuedTriviaGameStore3():

    timber: TimberInterface = TimberStub()

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    queuedTriviaGameStore: QueuedTriviaGameStoreInterface = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_clearQueuedSuperGames_withEmptyTwitchChannel(self):
        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames('imyt')
        assert clearResult.getAmountRemoved() == 0
        assert clearResult.getOldQueueSize() == 0

    def test_sanity(self):
        assert self.queuedTriviaGameStore is not None
        assert isinstance(self.queuedTriviaGameStore, QueuedTriviaGameStoreInterface)


class TestQueuedTriviaGameStore4():

    timber: TimberInterface = TimberStub()

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    queuedTriviaGameStore: QueuedTriviaGameStoreInterface = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    startNewSuperTriviaGameAction = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 1,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    @pytest.mark.asyncio
    async def test_addQueuedSuperGamesSize_withEmptyTwitchChannel_andSuperGameIsInProgress(self):
        assert self.startNewSuperTriviaGameAction.isQueueActionConsumed() is False

        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction
        )

        assert result.getAmountAdded() == 1
        assert result.getNewQueueSize() == 1
        assert result.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction.isQueueActionConsumed() is True

    def test_sanity(self):
        assert self.queuedTriviaGameStore is not None
        assert isinstance(self.queuedTriviaGameStore, QueuedTriviaGameStoreInterface)


class TestQueuedTriviaGameStore5():

    timber: TimberInterface = TimberStub()

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    queuedTriviaGameStore: QueuedTriviaGameStoreInterface = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    startNewSuperTriviaGameAction = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 5,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'stashiocat',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'stashiocat',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    @pytest.mark.asyncio
    async def test_addQueuedSuperGamesSize_withEmptyTwitchChannel_andSuperGameIsInProgress_andQueueActionConsumedIsTrue(self):
        assert self.startNewSuperTriviaGameAction.isQueueActionConsumed() is False

        result = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction
        )

        assert result.getAmountAdded() == 5
        assert result.getNewQueueSize() == 5
        assert result.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction.isQueueActionConsumed() is True

    def test_sanity(self):
        assert self.queuedTriviaGameStore is not None
        assert isinstance(self.queuedTriviaGameStore, QueuedTriviaGameStoreInterface)


class TestQueuedTriviaGameStore6():

    timber: TimberInterface = TimberStub()

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    queuedTriviaGameStore: QueuedTriviaGameStoreInterface = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    startNewSuperTriviaGameAction = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 3,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    @pytest.mark.asyncio
    async def test_clearQueuedSuperGames(self):
        assert self.startNewSuperTriviaGameAction.isQueueActionConsumed() is False

        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames(
            twitchChannel = self.startNewSuperTriviaGameAction.getTwitchChannel()
        )
        assert clearResult.getAmountRemoved() == 0
        assert clearResult.getOldQueueSize() == 0

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = False,
            action = self.startNewSuperTriviaGameAction
        )
        assert addResult.getAmountAdded() == 2
        assert addResult.getNewQueueSize() == 2
        assert addResult.getOldQueueSize() == 0
        assert self.startNewSuperTriviaGameAction.isQueueActionConsumed()

        queueSize = await self.queuedTriviaGameStore.getQueuedSuperGamesSize(
            twitchChannel = self.startNewSuperTriviaGameAction.getTwitchChannel()
        )
        assert queueSize == 2

        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames(
            twitchChannel = self.startNewSuperTriviaGameAction.getTwitchChannel()
        )
        assert clearResult.getAmountRemoved() == 2
        assert clearResult.getOldQueueSize() == 2

        queueSize = await self.queuedTriviaGameStore.getQueuedSuperGamesSize(
            twitchChannel = self.startNewSuperTriviaGameAction.getTwitchChannel()
        )
        assert queueSize == 0

    def test_sanity(self):
        assert self.queuedTriviaGameStore is not None
        assert isinstance(self.queuedTriviaGameStore, QueuedTriviaGameStoreInterface)


class TestQueuedTriviaGameStore7():

    timber: TimberInterface = TimberStub()

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    queuedTriviaGameStore: QueuedTriviaGameStoreInterface = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    startNewSuperTriviaGameAction = StartNewSuperTriviaGameAction(
        isQueueActionConsumed = False,
        isShinyTriviaEnabled = False,
        isToxicTriviaEnabled = False,
        numberOfGames = 1,
        perUserAttempts = 2,
        pointsForWinning = 25,
        regularTriviaPointsForWinning = 5,
        secondsToLive = 50,
        shinyMultiplier = 8,
        toxicMultiplier = 16,
        toxicTriviaPunishmentMultiplier = 0,
        twitchChannel = 'smCharles',
        triviaFetchOptions = TriviaFetchOptions(
            isJokeTriviaRepositoryEnabled = False,
            twitchChannel = 'smCharles',
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )
    )

    @pytest.mark.asyncio
    async def test_clearQueuedSuperGames_isCaseInsensitive(self):
        assert self.startNewSuperTriviaGameAction.isQueueActionConsumed() is False

        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames('smCharles')
        assert clearResult.getAmountRemoved() == 0
        assert clearResult.getOldQueueSize() == 0

        addResult = await self.queuedTriviaGameStore.addSuperGames(
            isSuperTriviaGameCurrentlyInProgress = True,
            action = self.startNewSuperTriviaGameAction
        )
        assert addResult.getAmountAdded() == 1
        assert addResult.getNewQueueSize() == 1
        assert addResult.getOldQueueSize() == 0

        queueSize = await self.queuedTriviaGameStore.getQueuedSuperGamesSize('smCharles')
        assert queueSize == 1

        queueSize = await self.queuedTriviaGameStore.getQueuedSuperGamesSize('smcharles')
        assert queueSize == 1

        clearResult = await self.queuedTriviaGameStore.clearQueuedSuperGames('smCharles')
        assert clearResult.getAmountRemoved() == 1
        assert clearResult.getOldQueueSize() == 1

        queueSize = await self.queuedTriviaGameStore.getQueuedSuperGamesSize('smcharles')
        assert queueSize == 0

    def test_sanity(self):
        assert self.queuedTriviaGameStore is not None
        assert isinstance(self.queuedTriviaGameStore, QueuedTriviaGameStoreInterface)
