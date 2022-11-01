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
    from ...trivia.triviaAnswerCheckResult import TriviaAnswerCheckResult
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
    from trivia.triviaAnswerCheckResult import TriviaAnswerCheckResult
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
            categoryId = None,
            emote = '🏫',
            question = 'Which of these Super Metroid players is a bully?',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.BONGO
        )

        result = await self.triviaAnswerChecker.checkAnswer('a', question)
        assert result is TriviaAnswerCheckResult.INCORRECT

        result = await self.triviaAnswerChecker.checkAnswer('b', question)
        assert result is TriviaAnswerCheckResult.INCORRECT

        result = await self.triviaAnswerChecker.checkAnswer('c', question)
        assert result is TriviaAnswerCheckResult.INCORRECT

        result = await self.triviaAnswerChecker.checkAnswer('d', question)
        assert result is TriviaAnswerCheckResult.CORRECT

        result = await self.triviaAnswerChecker.checkAnswer('e', question)
        assert result is TriviaAnswerCheckResult.INVALID_INPUT

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestionAndAnswerIsFalse(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ False ],
            category = None,
            categoryId = None,
            emote = '🏫',
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.BONGO
        )

        result = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is TriviaAnswerCheckResult.CORRECT

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is TriviaAnswerCheckResult.INCORRECT

        result = await self.triviaAnswerChecker.checkAnswer('blah', question)
        assert result is TriviaAnswerCheckResult.INVALID_INPUT

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestionAndAnswerIsTrue(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ True ],
            category = None,
            categoryId = None,
            emote = '🏫',
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.BONGO
        )

        result = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is TriviaAnswerCheckResult.INCORRECT

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is TriviaAnswerCheckResult.CORRECT

        result = await self.triviaAnswerChecker.checkAnswer('qwerty', question)
        assert result is TriviaAnswerCheckResult.INVALID_INPUT

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestionAndAnswerIsTrueAndFalse(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ True, False ],
            category = None,
            categoryId = None,
            emote = '🏫',
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.BONGO
        )

        result = await self.triviaAnswerChecker.checkAnswer('f', question)
        assert result is TriviaAnswerCheckResult.CORRECT

        result = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is TriviaAnswerCheckResult.CORRECT

        result = await self.triviaAnswerChecker.checkAnswer('t', question)
        assert result is TriviaAnswerCheckResult.CORRECT

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is TriviaAnswerCheckResult.CORRECT

        result = await self.triviaAnswerChecker.checkAnswer('wasd', question)
        assert result is TriviaAnswerCheckResult.INVALID_INPUT

    @pytest.mark.asyncio
    async def test_checkAnswer_withTrueFalseQuestion(self):
        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = [ True ],
            category = None,
            categoryId = None,
            emote = '🏫',
            question = 'The Super Metroid player stashiocat is a Chicago Bully.',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.BONGO
        )

        result = await self.triviaAnswerChecker.checkAnswer('false', question)
        assert result is TriviaAnswerCheckResult.INCORRECT

        result = await self.triviaAnswerChecker.checkAnswer('true', question)
        assert result is TriviaAnswerCheckResult.CORRECT

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion(self):
        print(dir(TriviaSettingsRepository))
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['North Korea'],
                cleanedCorrectAnswers=['north korea'],
                category='Test Category',
                categoryId=None,
                emote = '🏫',
                question='The Korean country farthest north.',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('north korea', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('norths korea', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('north koreas', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('south korea', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('sorth korea', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('nouth korea', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

    @pytest.mark.asyncio
    async def test_checkAnswer_withParentheticalQuestionAnswerQuestion(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['(Kurt) Vonnegut (Jr.)'],
                cleanedCorrectAnswers=['kurt vonnegut jr', 'kurt vonnegut', 'vonnegut', 'vonnegut jr'],
                category='Test Category',
                categoryId=None,
                emote = '🏫',
                question='That one weird author guy',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('kurt vonnegut', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('vonnegut', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('vonegut', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('kurt vonnegut jr', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('kurt vonnegut junior', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('kurt voneguit', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_withDecades(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            correctAnswer = await self.triviaAnswerCompiler.compileTextAnswer('1950s')

            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=[correctAnswer],
                cleanedCorrectAnswers=await self.triviaAnswerCompiler.expandNumerals(correctAnswer),
                category='Test Category',
                categoryId=None,
                emote = '🏫',
                question='In what decade did that one thing come out?',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('1850', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1850s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1900', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1900s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1910', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1910s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1920', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1920s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1930', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1930s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1940', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1940s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1948', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1948s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1949', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1949s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1950', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1950s', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1951', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1951s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1952', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1952s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1953', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1953s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1954', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1954s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1955', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1955s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1956', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1956s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1957', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1957s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1958', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1958s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1959', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1959s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1960', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1960s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1970', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1970s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1980', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1980s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1990', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1990s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('2000', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('2000s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('2050', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('2050s', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

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
                categoryId=None,
                emote = '🏫',
                question='Shakespeare wrote a play about him once or something...',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('richard the third', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('richard 3rd', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('richard three', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('king richard III', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('richard iii', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('king richard the 3rd', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('king richard 4', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('king richard 30', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_withSpaces(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['Beach Ball'],
                cleanedCorrectAnswers=['beach ball'],
                category='Test Category',
                categoryId=None,
                emote = '🏫',
                question='Shakespeare wrote a play about him once or something...',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('beach ball', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('beachball', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('beach balls', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('beachballs', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('a beach ball', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('beach ball s', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('beach es ball s', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('beachballa', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('beach balla', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('green beach ball', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

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
                categoryId=None,
                emote = '🏫',
                question='What year is that one year people say a lot when talking about fascism and whatnot?',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('1984', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('nineteen eightyfour', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('MCMLXXXIV', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('1985', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

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
                categoryId=None,
                emote = '🏫',
                question='Christmas is on which day of the month of December?',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('the twenty fifth', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('25', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('twenty five', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('24', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('twenty forth', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

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
                categoryId=None,
                emote = '🏫',
                question='Name a food coloring',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('red dye #5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('red dye number 5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('red dye no 5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('red number 5', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

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
                categoryId=None,
                emote = '🏫',
                question='Name a food coloring',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('x=5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('x = 5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('five', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('x is 5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('x equals 5', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('x = 5.0', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

    @pytest.mark.asyncio
    async def test_checkAnswer_withQuestionAnswerQuestion_withTheNewMath(self):
        with mock.patch.object(TriviaSettingsRepository, '_TriviaSettingsRepository__readJson', mockSettingsJSON):
            question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
                correctAnswers=['The New Math'],
                cleanedCorrectAnswers=['new math'],
                category='Test Category',
                categoryId=None,
                emote = '🏫',
                question='Something about math',
                triviaId='abc123',
                triviaDifficulty=TriviaDifficulty.UNKNOWN,
                triviaSource=TriviaSource.J_SERVICE,
            )

            result = await self.triviaAnswerChecker.checkAnswer('new math', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('the new math', question)
            assert result is TriviaAnswerCheckResult.CORRECT

            result = await self.triviaAnswerChecker.checkAnswer('the', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('math', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('new', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('math new', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('the math', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

            result = await self.triviaAnswerChecker.checkAnswer('the new', question)
            assert result is TriviaAnswerCheckResult.INCORRECT

    def test_sanity(self):
        assert self.triviaAnswerChecker is not None
        assert isinstance(self.triviaAnswerChecker, TriviaAnswerChecker)
