from typing import List

import pytest

try:
    from ...trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from ...trivia.triviaExceptions import BadTriviaAnswerException
except:
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaExceptions import BadTriviaAnswerException


class TestTriviaAnswerCompiler():

    triviaAnswerCompiler: TriviaAnswerCompiler = TriviaAnswerCompiler()

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withEmptyString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileBoolAnswer('')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withFalse(self):
        result: bool = await self.triviaAnswerCompiler.compileBoolAnswer('false')
        assert result is False

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withNone(self):
        result: bool = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileBoolAnswer(None)
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withWhitespaceString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileBoolAnswer(' ')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withTrue(self):
        result: bool = await self.triviaAnswerCompiler.compileBoolAnswer('true')
        assert result is True

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withA(self):
        result: int = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('A')
        assert result == 0

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('a')
        assert result == 0

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withB(self):
        result: int = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('B')
        assert result == 1

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('b')
        assert result == 1

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withC(self):
        result: int = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('C')
        assert result == 2

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('c')
        assert result == 2

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withD(self):
        result: int = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('D')
        assert result == 3

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('d')
        assert result == 3

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withDigit(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('0')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withE(self):
        result: int = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('E')
        assert result == 4

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('e')
        assert result == 4

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withF(self):
        result: int = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('F')
        assert result == 5

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('f')
        assert result == 5

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withEmptyString(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withNone(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal(None)
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withSymbol(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('=')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withWhitespaceString(self):
        result: int = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal(' ')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withZ(self):
        result: int = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('Z')
        assert result == 25

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('z')
        assert result == 25

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withEmptyString(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('')
        assert result == ''

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withHelloWorld(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('Hello, World!')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withNone(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer(None)
        assert result == ''

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withWhitespaceString(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer(' ')
        assert result == ''

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withDuplicateWords(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'hello', 'Hello', 'HELLO', 'world', 'World', 'World!' ])
        assert result is not None
        assert len(result) == 2
        assert 'hello' in result
        assert 'world' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withEddieVanHalen(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '(Eddie) Van Halen' ])
        assert result is not None
        assert len(result) == 2
        assert 'eddie van halen' in result
        assert 'van halen' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withEmptyList(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList(list())
        assert result is not None
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withNone(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList(None)
        assert result is not None
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withKurtVonnegutJr(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '(Kurt) Vonnegut (Jr.)' ])
        assert result is not None
        assert len(result) == 4
        assert 'kurt vonnegut jr' in result
        assert 'kurt vonnegut' in result
        assert 'vonnegut' in result
        assert 'vonnegut jr' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withNumberWord(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'three' ])
        assert result is not None
        assert len(result) == 2
        assert 'three' in result
        assert '3' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withNumberWords(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'one', 'two' ])
        assert result is not None
        assert len(result) == 4
        assert 'one' in result
        assert '1' in result
        assert 'two' in result
        assert '2' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withOrdinalWord(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'third' ])
        assert result is not None
        assert len(result) == 2
        assert 'third' in result
        assert '3rd' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withOrdinalWords(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'first', 'second' ])
        assert result is not None
        assert len(result) == 4
        assert 'first' in result
        assert '1st' in result
        assert 'second' in result
        assert '2nd' in result

    def test_sanity(self):
        assert self.triviaAnswerCompiler is not None
        assert isinstance(self.triviaAnswerCompiler, TriviaAnswerCompiler)
