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
        result: bool = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileBoolAnswer('')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withFalse(self):
        result: bool = await self.__triviaAnswerCompiler.compileBoolAnswer('false')
        assert result is False

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withNone(self):
        result: bool = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileBoolAnswer(None)
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withWhitespaceString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileBoolAnswer(' ')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withTrue(self):
        result: bool = await self.__triviaAnswerCompiler.compileBoolAnswer('true')
        assert result is True

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withA(self):
        result: int = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('A')
        assert result == 0

        result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('a')
        assert result == 0

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withB(self):
        result: int = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('B')
        assert result == 1

        result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('b')
        assert result == 1

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withC(self):
        result: int = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('C')
        assert result == 3

        result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('c')
        assert result == 3

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withD(self):
        result: int = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('D')
        assert result == 4

        result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('d')
        assert result == 4

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withDigit(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('0')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withE(self):
        result: int = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('E')
        assert result == 5

        result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('e')
        assert result == 5

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withF(self):
        result: int = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('F')
        assert result == 6

        result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('f')
        assert result == 6

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withEmptyString(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withNone(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal(None)
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withSymbol(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('=')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withWhitespaceString(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal(' ')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withZ(self):
        result: int = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('Z')
        assert result == 26

        result = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('z')
        assert result == 26

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withEmptyString(self):
        result: str = await self.__triviaAnswerCompiler.compileTextAnswer('')
        assert result == ''

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withHelloWorld(self):
        result: str = await self.__triviaAnswerCompiler.compileTextAnswer('Hello, World!')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withNone(self):
        result: str = await self.__triviaAnswerCompiler.compileTextAnswer(None)
        assert result == ''

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withWhitespaceString(self):
        result: str = await self.__triviaAnswerCompiler.compileTextAnswer(' ')
        assert result == ''

    def test_sanity(self):
        assert isinstance(self.__triviaAnswerCompiler, TriviaAnswerCompiler)
