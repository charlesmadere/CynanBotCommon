import pytest

try:
    from ...trivia.absTriviaGameState import AbsTriviaGameState
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
    from trivia.absTriviaGameState import AbsTriviaGameState
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
        triviaSource = TriviaSource.WILL_FRY_TRIVIA_API
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

    superQuestion1: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
        correctAnswers = [ 'Chicago Bullies' ],
        cleanedCorrectAnswers = [ 'chicago bullies' ],
        category = None,
        categoryId = None,
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
        question = 'This player forgot to fight Phantoon in a randomizer match.',
        triviaId = 'jkl012',
        triviaDifficulty = TriviaDifficulty.UNKNOWN,
        triviaSource = TriviaSource.J_SERVICE
    )

    triviaGameStore = TriviaGameStore()

    @pytest.mark.asyncio
    async def test_add(self):
        game1: AbsTriviaGameState = TriviaGameState(
            triviaQuestion = self.normalQuestion1,
            pointsForWinning = 5,
            secondsToLive = 60,
            twitchChannel = 'smCharles',
            userId = '123456',
            userName = 'Eddie'
        )

        await self.triviaGameStore.add(game1)

        games = await self.triviaGameStore.getAll()
        assert len(games) == 1
        assert game1 in games

        games = await self.triviaGameStore.getNormalGames()
        assert len(games) == 1
        assert game1 in games

        games = await self.triviaGameStore.getSuperGames()
        assert len(games) == 0
        assert game1 not in games

        game2: AbsTriviaGameState = SuperTriviaGameState(
            triviaQuestion = self.superQuestion1,
            perUserAttempts = 2,
            pointsForWinning = 25,
            pointsMultiplier = 5,
            secondsToLive = 60,
            twitchChannel = 'smCharles'
        )

        await self.triviaGameStore.add(game2)

        games = await self.triviaGameStore.getAll()
        assert len(games) == 2
        assert game1 in games
        assert game2 in games

        games = await self.triviaGameStore.getNormalGames()
        assert len(games) == 1
        assert game1 in games
        assert game2 not in games

        games = await self.triviaGameStore.getSuperGames()
        assert len(games) == 1
        assert game1 not in games
        assert game2 in games

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
    async def test_getNormalGames_isEmptyList(self):
        games = await self.triviaGameStore.getNormalGames()
        assert len(games) == 0

    @pytest.mark.asyncio
    async def test_getSuperGame_isNone(self):
        game = await self.triviaGameStore.getSuperGame(
            twitchChannel = 'smCharles'
        )

        assert game is None

    @pytest.mark.asyncio
    async def test_getSuperGames_isEmptyList(self):
        games = await self.triviaGameStore.getSuperGames()
        assert len(games) == 0

    def test_sanity(self):
        assert self.triviaGameStore is not None
        assert isinstance(self.triviaGameStore, TriviaGameStore)
