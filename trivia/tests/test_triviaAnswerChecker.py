import pytest

try:
    from ...trivia.absTriviaQuestion import AbsTriviaQuestion
    from ...trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from ...trivia.triviaAnswerChecker import TriviaAnswerChecker
    from ...trivia.triviaDifficulty import TriviaDifficulty
    from ...trivia.triviaSource import TriviaSource
    from ...trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion
except:
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaAnswerChecker import TriviaAnswerChecker
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSource import TriviaSource
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TestTriviaAnswerChecker():

    triviaAnswerChecker: TriviaAnswerChecker = TriviaAnswerChecker()

    @pytest.mark.asyncio
    async def test_checkAnswer_withMultipleChoiceQuestionAndAnswerIsA(self):
        question: AbsTriviaQuestion = MultipleChoiceTriviaQuestion(
            correctAnswers = [ 'stashiocat' ],
            multipleChoiceResponses = [ 'Eddie', 'Imyt', 'smCharles', 'stashiocat' ],
            category = None,
            question = 'Which of these Super Metroid players is a bully?',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource[0]
        )

        result: bool = await self.triviaAnswerChecker.checkAnswer('a', question)
        assert result is False

        result = await self.triviaAnswerChecker.checkAnswer('b', question)
        assert result is False

        result = await self.triviaAnswerChecker.checkAnswer('c', question)
        assert result is False

        result = await self.triviaAnswerChecker.checkAnswer('d', question)
        assert result is True

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestionAndAnswerIsFalse(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ False ],
            category = None,
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource[0]
        )

        result: bool = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is True

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestionAndAnswerIsTrue(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ True ],
            category = None,
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource[0]
        )

        result: bool = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is False

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is True

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestionAndAnswerIsTrueAndFalse(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ True, False ],
            category = None,
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource[0]
        )

        result: bool = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is True

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is True

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestion(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ True ],
            category = None,
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource[0]
        )

        result: bool = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is False

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is True

    def test_sanity(self):
        assert self.triviaAnswerChecker is not None
        assert isinstance(self.triviaAnswerChecker, TriviaAnswerChecker)