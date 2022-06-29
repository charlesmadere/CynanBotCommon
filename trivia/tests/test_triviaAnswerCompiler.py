import pytest

try:
    from ...trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from ...trivia.triviaExceptions import BadTriviaAnswerException
except:
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaExceptions import BadTriviaAnswerException


class TestTriviaAnswerCompiler():

    __triviaAnswerCompiler: TriviaAnswerCompiler = TriviaAnswerCompiler()

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withEmptyString(self):
        exception: Exception = None
        result: bool = None

        try:
            result = await self.__triviaAnswerCompiler.compileBoolAnswer('')
        except Exception as e:
            exception = e

        assert isinstance(exception, BadTriviaAnswerException)
        assert result is None

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withFalse(self):
        result: bool = await self.__triviaAnswerCompiler.compileBoolAnswer('false')
        assert result is False

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withNone(self):
        exception: Exception = None
        result: bool = None

        try:
            result = await self.__triviaAnswerCompiler.compileBoolAnswer(None)
        except Exception as e:
            exception = e

        assert isinstance(exception, BadTriviaAnswerException)
        assert result is None

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withWhitespaceString(self):
        exception: Exception = None
        result: bool = None

        try:
            result = await self.__triviaAnswerCompiler.compileBoolAnswer(' ')
        except Exception as e:
            exception = e

        assert isinstance(exception, BadTriviaAnswerException)
        assert result is None

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withTrue(self):
        result: bool = await self.__triviaAnswerCompiler.compileBoolAnswer('true')
        assert result is True

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withNone(self):
        result: str = await self.__triviaAnswerCompiler.compileTextAnswer(None)
        assert result == ''

    def test_sanity(self):
        assert isinstance(self.__triviaAnswerCompiler, TriviaAnswerCompiler)
