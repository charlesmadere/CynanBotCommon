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
    async def test_compileBoolAnswer_withNone(self):
        exception: Exception = None
        result: bool = None

        try:
            result = await self.__triviaAnswerCompiler.compileBoolAnswer(None)
        except Exception as e:
            exception = e

        assert isinstance(exception, BadTriviaAnswerException)
        assert result is None        

    def test_sanity(self):
        assert isinstance(self.__triviaAnswerCompiler, TriviaAnswerCompiler)
