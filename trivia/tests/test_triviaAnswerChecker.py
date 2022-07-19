import asyncio
from asyncio import AbstractEventLoop

import mock
import pytest

try:
    from ...timber.timber import Timber
    from ...trivia.absTriviaQuestion import AbsTriviaQuestion
    from ...trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from ...trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from ...trivia.triviaAnswerChecker import TriviaAnswerChecker
    from ...trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from ...trivia.triviaDifficulty import TriviaDifficulty
    from ...trivia.triviaSettingsRepository import TriviaSettingsRepository
    from ...trivia.triviaSource import TriviaSource
    from ...trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion
except:
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaAnswerChecker import TriviaAnswerChecker
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


async def mockSettingsJSON(cls, *args, **kwargs):
    return {}


class TestTriviaAnswerChecker():

    eventLoop: AbstractEventLoop = asyncio.get_event_loop()
    timber: Timber = Timber(
        eventLoop = eventLoop
    )
    triviaAnswerCompiler: TriviaAnswerCompiler = TriviaAnswerCompiler()
    triviaSettingsRepository: TriviaSettingsRepository = TriviaSettingsRepository()

    triviaAnswerChecker: TriviaAnswerChecker = TriviaAnswerChecker(
        timber = timber,
        triviaAnswerCompiler = triviaAnswerCompiler,
        triviaSettingsRepository = triviaSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_checkAnswer_withMultipleChoiceQuestionAndAnswerIsA(self):
        question: AbsTriviaQuestion = MultipleChoiceTriviaQuestion(
            correctAnswers = [ 'stashiocat' ],
            multipleChoiceResponses = [ 'Eddie', 'Imyt', 'smCharles', 'stashiocat' ],
            category = None,
            question = 'Which of these Super Metroid players is a bully?',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.BONGO
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
            triviaSource = TriviaSource.BONGO
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
            triviaSource = TriviaSource.BONGO
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
            triviaSource = TriviaSource.BONGO
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
            triviaSource = TriviaSource.BONGO
        )

        result: bool = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is False

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is True

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion(self):
        print(dir(TriviaSettingsRepository))
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['North Korea'],
                cleanedCorrectAnswers=['north korea'],
                category='Test Category',
                question='the correct korea',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )
            result: bool = await self.triviaAnswerChecker.checkAnswer('north korea', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('norths korea', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('north koreas', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('south korea', question)
            assert result is False

            result = await self.triviaAnswerChecker.checkAnswer('sorth korea', question)
            assert result is False

            result = await self.triviaAnswerChecker.checkAnswer('nouth korea', question)
            assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withParentheticalQuestionAnswerQuestion(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['(Kurt) Vonnegut (Jr.)'],
                cleanedCorrectAnswers=['kurt vonnegut jr', 'kurt vonnegut', 'vonnegut', 'vonnegut jr'],
                category='Test Category',
                question='That one weird author guy',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )
            result: bool = await self.triviaAnswerChecker.checkAnswer('kurt vonnegut', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('vonnegut', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('vonegut', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('kurt vonnegut jr', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('kurt vonnegut junior', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('kurt voneguit', question)
            assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_withDigits(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['(King) Richard III'],
                cleanedCorrectAnswers=[
                    'richard three',
                    'richard third',
                    'richard the third',
                    'king richard three',
                    'king richard third',
                    'king richard the third',
                ],
                category='Test Category',
                question='Shakespeare wrote a play about him once or something...',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )
            result: bool = await self.triviaAnswerChecker.checkAnswer('richard the third', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('richard 3rd', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('richard three', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('king richard III', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('richard iii', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('king richard the 3rd', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('king richard 4', question)
            assert result is False

            result = await self.triviaAnswerChecker.checkAnswer('king richard 30', question)
            assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_withSpaces(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['Beach Ball'],
                cleanedCorrectAnswers=['beach ball'],
                category='Test Category',
                question='Shakespeare wrote a play about him once or something...',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )
            result: bool = await self.triviaAnswerChecker.checkAnswer('beach ball', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('beachball', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('beach balls', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('beachballs', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('a beach ball', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('beach ball s', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('beach es ball s', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('beachballa', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('beach balla', question)
            assert result is False

            result = await self.triviaAnswerChecker.checkAnswer('green beach ball', question)
            assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_numberOnly(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['1984'],
                cleanedCorrectAnswers=[
                    'nineteen eighty four',
                    'one nine eight four',
                    'one thousand nine hundred eighty four',
                    'one thousand nine hundred eighty fourth',
                    'the one thousand nine hundred eighty fourth',
                ],
                category='Test Category',
                question='What year is that one year people say a lot when talking about fascism and whatnot?',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )
            result: bool = await self.triviaAnswerChecker.checkAnswer('1984', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('nineteen eightyfour', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('MCMLXXXIV', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('1985', question)
            assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_ordinalOnly(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['25th'],
                cleanedCorrectAnswers=[
                    'twenty five',
                    'two five',
                    'twenty fifth',
                    'the twenty fifth',
                ],
                category='Test Category',
                question='Christmas is on which day of the month of December?',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )
            result: bool = await self.triviaAnswerChecker.checkAnswer('the twenty fifth', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('25', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('twenty five', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('24', question)
            assert result is False

            result = await self.triviaAnswerChecker.checkAnswer('twenty forth', question)
            assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_withHash(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['Red Dye #5'],
                cleanedCorrectAnswers=[
                    'red dye five',
                    'red dye fifth',
                    'red dye the fifth',
                    'red dye number five',
                    'red dye number fifth',
                    'red dye number the fifth',
                ],
                category='Test Category',
                question='Name a food coloring',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result: bool = await self.triviaAnswerChecker.checkAnswer('red dye #5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('red dye number 5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('red dye no 5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('red number 5', question)
            assert result is False

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_withEquation(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['X=5'],
                cleanedCorrectAnswers=[
                    'x five',
                    'x fifth',
                    'x the fifth',
                    'five',
                    'fifth',
                    'the fifth',
                    'x is five',
                    'x is fifth',
                    'x is the fifth',
                    'x equals five',
                    'x equals fifth',
                    'x equals the fifth',
                ],
                category='Test Category',
                question='Name a food coloring',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result: bool = await self.triviaAnswerChecker.checkAnswer('x=5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('x = 5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('five', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('x is 5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('x equals 5', question)
            assert result is True

            result = await self.triviaAnswerChecker.checkAnswer('x = 5.0', question)
            assert result is False

    def test_sanity(self):
        assert self.triviaAnswerChecker is not None
        assert isinstance(self.triviaAnswerChecker, TriviaAnswerChecker)
