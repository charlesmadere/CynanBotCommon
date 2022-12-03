import pytest

try:
    from ...trivia.absTriviaQuestion import AbsTriviaQuestion
    from ...trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from ...trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from ...trivia.superTriviaGameState import SuperTriviaGameState
    from ...trivia.triviaDifficulty import TriviaDifficulty
    from ...trivia.triviaGameState import TriviaGameState
    from ...trivia.triviaGameStore import TriviaGameStore
    from ...trivia.triviaSource import TriviaSource
    from ...trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion
except:
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.superTriviaGameState import SuperTriviaGameState
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaGameStore import TriviaGameStore
    from trivia.triviaSource import TriviaSource
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TriviaGameStoreTests():

    normalQuestion1: AbsTriviaQuestion = MultipleChoiceTriviaQuestion(
        correctAnswers = [ 'Chicago Bullies' ],
        multipleChoiceResponses = [ 'Chicago Bullies', 'Chicago Bulls', 'Minnesota Chipmunks' ],
        category = None,
        categoryId = None,
        emote = '😎',
        question = 'What team is stashiocat a member of?',
        triviaId = 'abc123',
        triviaDifficulty = TriviaDifficulty.UNKNOWN,
        triviaSource = TriviaSource.WILL_FRY_TRIVIA
    )

    normalQuestion2: AbsTriviaQuestion = TrueFalseTriviaQuestion(
        correctAnswers = [ True ],
        category = None,
        categoryId = None,
        emote = '😎',
        question = 'Is stashiocat a member of the Chicago Bullies?',
        triviaId = 'def456',
        triviaDifficulty = TriviaDifficulty.UNKNOWN,
        triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
    )

    normalQuestion3: AbsTriviaQuestion = MultipleChoiceTriviaQuestion(
        correctAnswers = [ 'Nintendo' ],
        multipleChoiceResponses = [ 'Microsoft', 'Nintendo', 'Sega', 'Sony' ],
        category = None,
        categoryId = None,
        emote = '😎',
        question = 'Which company made the SNES?',
        triviaId = 'xyz321',
        triviaDifficulty = TriviaDifficulty.UNKNOWN,
        triviaSource = TriviaSource.MILLIONAIRE
    )

    superQuestion1: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
        correctAnswers = [ 'Chicago Bullies' ],
        cleanedCorrectAnswers = [ 'chicago bullies' ],
        category = None,
        categoryId = None,
        emote = '😎',
        question = 'One of this team\'s members is stashiocat.',
        triviaId = 'ghi789',
        triviaDifficulty = TriviaDifficulty.UNKNOWN,
        triviaSource = TriviaSource.FUNTOON
    )

    superQuestion2: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
        correctAnswers = [ 'stashiocat' ],
        cleanedCorrectAnswers = [ 'stashiocat' ],
        category = None,
        categoryId = None,
        emote = '😎',
        question = 'This player forgot to fight Phantoon in a randomizer match.',
        triviaId = 'jkl012',
        triviaDifficulty = TriviaDifficulty.UNKNOWN,
        triviaSource = TriviaSource.J_SERVICE
    )

    game1 = TriviaGameState(
        triviaQuestion = normalQuestion1,
        pointsForWinning = 5,
        secondsToLive = 60,
        actionId = 'abc123',
        twitchChannel = 'smCharles',
        userId = '111111',
        userName = 'Eddie'
    )

    game2 = TriviaGameState(
        triviaQuestion = normalQuestion2,
        pointsForWinning = 5,
        secondsToLive = 60,
        actionId = 'abc123',
        twitchChannel = 'smCharles',
        userId = '222222',
        userName = 'stashiocat'
    )

    game3 = TriviaGameState(
        triviaQuestion = normalQuestion3,
        pointsForWinning = 5,
        secondsToLive = 60,
        actionId = 'abc123',
        twitchChannel = 'Imyt',
        userId = '222222',
        userName = 'stashiocat'
    )

    game4 = SuperTriviaGameState(
        triviaQuestion = superQuestion1,
        perUserAttempts = 2,
        pointsForWinning = 25,
        pointsMultiplier = 5,
        secondsToLive = 60,
        actionId = 'abc123',
        twitchChannel = 'smCharles'
    )

    game5 = SuperTriviaGameState(
        triviaQuestion = superQuestion2,
        perUserAttempts = 2,
        pointsForWinning = 25,
        pointsMultiplier = 5,
        secondsToLive = 60,
        actionId = 'abc123',
        twitchChannel = 'Imyt'
    )

    triviaGameStore = TriviaGameStore()

    @pytest.mark.asyncio
    async def test_add(self):
        await self.triviaGameStore.add(self.game1)

        games = await self.triviaGameStore.getAll()
        assert len(games) == 1
        assert self.game1 in games

        games = await self.triviaGameStore.getNormalGames()
        assert len(games) == 1
        assert self.game1 in games

        games = await self.triviaGameStore.getSuperGames()
        assert len(games) == 0
        assert self.game1 not in games

        await self.triviaGameStore.add(self.game4)

        games = await self.triviaGameStore.getAll()
        assert len(games) == 2
        assert self.game1 in games
        assert self.game4 in games

        games = await self.triviaGameStore.getNormalGames()
        assert len(games) == 1
        assert self.game1 in games
        assert self.game4 not in games

        games = await self.triviaGameStore.getSuperGames()
        assert len(games) == 1
        assert self.game1 not in games
        assert self.game4 in games

    @pytest.mark.asyncio
    async def test_getAll_isEmptyList(self):
        games = await self.triviaGameStore.getAll()
        assert len(games) == 0

    @pytest.mark.asyncio
    async def test_getNormalGame_isNone(self):
        game = await self.triviaGameStore.getNormalGame(
            twitchChannel = 'smCharles',
            userName = 'stashiocat'
        )

        assert game is None

    @pytest.mark.asyncio
    async def test_getNormalGames_withEmptyTriviaGameStore_returnsEmptyList(self):
        games = await self.triviaGameStore.getNormalGames()
        assert len(games) == 0

    @pytest.mark.asyncio
    async def test_getSuperGame_withEmptyTriviaGameStore_returnsNone(self):
        game = await self.triviaGameStore.getSuperGame(
            twitchChannel = 'smCharles'
        )

        assert game is None

    @pytest.mark.asyncio
    async def test_getSuperGames_withEmptyTriviaGameStoree_returnsEmptyList(self):
        games = await self.triviaGameStore.getSuperGames()
        assert len(games) == 0

    @pytest.mark.asyncio
    async def test_remove(self):
        # removing a game from an empty TriviaGameStore should do nothing
        result = await self.triviaGameStore.removeNormalGame(
            twitchChannel = self.game1.getTwitchChannel(),
            userId = self.game1.getUserId()
        )
        assert result is False

        await self.triviaGameStore.add(self.game1)
        await self.triviaGameStore.add(self.game2)
        await self.triviaGameStore.add(self.game4)

        games = await self.triviaGameStore.getAll()
        assert len(games) == 3
        assert self.game1 in games
        assert self.game2 in games
        assert self.game4 in games

        # try removing a game that does not exist
        result = await self.triviaGameStore.removeNormalGame(
            twitchChannel = self.game2.getTwitchChannel(),
            userId = self.game1.getUserId()
        )
        assert result is False

        games = await self.triviaGameStore.getAll()
        assert len(games) == 3
        assert self.game1 in games
        assert self.game2 in games
        assert self.game4 in games

        # remove a game that does exist
        result = await self.triviaGameStore.removeNormalGame(
            twitchChannel = self.game2.getTwitchChannel(),
            userId = self.game2.getUserId()
        )
        assert result is True

        games = await self.triviaGameStore.getAll()
        assert len(games) == 2
        assert self.game1 in games
        assert self.game4 in games

        # remove another game that does exist
        result = await self.triviaGameStore.removeNormalGame(
            twitchChannel = self.game1.getTwitchChannel(),
            userId = self.game1.getUserId()
        )
        assert result is True

        games = await self.triviaGameStore.getAll()
        assert len(games) == 1
        assert self.game4 in games

        # try one more time to remove the same game that was just removed
        result = await self.triviaGameStore.removeNormalGame(
            twitchChannel = self.game1.getTwitchChannel(),
            userId = self.game1.getUserId()
        )
        assert result is False

        games = await self.triviaGameStore.getAll()
        assert len(games) == 1
        assert self.game4 in games

        # try removing an super trivia game that does not exist
        result = await self.triviaGameStore.removeSuperGame(
            twitchChannel = self.game5.getTwitchChannel()
        )
        assert result is False

        games = await self.triviaGameStore.getAll()
        assert len(games) == 1
        assert self.game4 in games

        # remove the final super trivia game
        result = await self.triviaGameStore.removeSuperGame(
            twitchChannel = self.game4.getTwitchChannel()
        )
        assert result is True

        games = await self.triviaGameStore.getAll()
        assert len(games) == 0

    @pytest.mark.asyncio
    async def test_removeNormalGame_withEmptyTriviaGameStore_returnsFalse(self):
        result = await self.triviaGameStore.removeNormalGame(
            twitchChannel = self.game3.getTwitchChannel(),
            userId = self.game3.getUserId()
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_removeSuperGame_withEmptyTriviaGameStore_returnsFalse(self):
        result = await self.triviaGameStore.removeSuperGame(
            twitchChannel = self.game5.getTwitchChannel()
        )

        assert result is False

    def test_sanity(self):
        assert self.triviaGameStore is not None
        assert isinstance(self.triviaGameStore, TriviaGameStore)
