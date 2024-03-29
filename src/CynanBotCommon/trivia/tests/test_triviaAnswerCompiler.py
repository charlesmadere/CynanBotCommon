from typing import List, Optional

import pytest

try:
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ..triviaAnswerCompiler import TriviaAnswerCompiler
    from ..triviaExceptions import BadTriviaAnswerException
except:
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaExceptions import BadTriviaAnswerException


class TestTriviaAnswerCompiler():

    timber: TimberInterface = TimberStub()

    triviaAnswerCompiler = TriviaAnswerCompiler(
        timber = timber
    )

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
    async def test_compileBoolAnswer_withF(self):
        result: bool = await self.triviaAnswerCompiler.compileBoolAnswer('f')
        assert result is False

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withFalse(self):
        result: bool = await self.triviaAnswerCompiler.compileBoolAnswer('false')
        assert result is False

    @pytest.mark.asyncio
    async def test_compileBoolAnswer_withNewLineString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = await self.triviaAnswerCompiler.compileBoolAnswer('\n')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, BadTriviaAnswerException)

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
    async def test_compileBoolAnswer_withT(self):
        result: bool = await self.triviaAnswerCompiler.compileBoolAnswer('t')
        assert result is True

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
    async def test_compileMultipleChoiceAnswer_withBracedA(self):
        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[A]')
        assert result == 0

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[a]')
        assert result == 0

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withBracedB(self):
        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[B]')
        assert result == 1

        result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[b]')
        assert result == 1

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withBracedDigit(self):
        result: Optional[int] = None
        exception: Optional[Exception] = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[1]')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, Exception)

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[0]')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, Exception)

    @pytest.mark.asyncio
    async def test_compileMultipleChoiceAnswer_withBracedWord(self):
        result: Optional[int] = None
        exception: Optional[Exception] = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[hello]')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, Exception)

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[world]')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, Exception)

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
    async def test_compileMultipleChoiceAnswer_withEmptyBraces(self):
        result: Optional[int] = None
        exception: Optional[Exception] = None

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[]')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, Exception)

        try:
            result = await self.triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal('[]')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, Exception)

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
    async def test_compileTextAnswer_withAmpersand(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('Between the Buried & Me')
        assert result == 'between the buried and me'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withEmptyString(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('')
        assert result == ''

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withHelloWorld(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('Hello, World!')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withNewLines(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('\nDream Theater\nOctavarium\n')
        assert result == 'dream theater octavarium'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withNone(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer(None)
        assert result == ''

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withPrefixA(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('A View From the Top of the World')
        assert result == 'view from the top of the world'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withPrefixAn(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('An Orange')
        assert result == 'orange'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withSaintNicholas(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('Saint Nicholas')
        assert result == 'saint nicholas'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withSirPeter(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('Sir Peter')
        assert result == 'sir peter'

    @pytest.mark.asyncio
    async def test_compileTextAnswer_withToRun(self):
        result: str = await self.triviaAnswerCompiler.compileTextAnswer('to run')
        assert result == 'run'

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
    async def test_compileTextAnswersList_withGeorgeSchultz(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'George P. Schultz' ])
        assert result is not None
        assert len(result) == 2
        assert 'george p schultz' in result
        assert 'george schultz' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withGroanGrown(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'groan/grown' ])
        assert result is not None
        assert len(result) == 3
        assert 'groangrown' in result
        assert 'groan' in result
        assert 'grown' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withHash(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'mambo #5' ])
        assert result is not None
        assert len(result) == 2
        assert 'mambo number 5' in result
        assert 'mambo 5' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withHeIsAVampire(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'he is a vampire' ])
        assert result is not None
        assert len(result) == 2
        assert 'he is a vampire' in result
        assert 'vampire' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withHesAVampire(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'he\'s a vampire' ])
        assert result is not None
        assert len(result) == 2
        assert 'hes a vampire' in result
        assert 'vampire' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withHelloWorld123(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'hello/world/123' ])
        assert result is not None
        assert len(result) == 4
        assert 'helloworld123' in result
        assert 'hello' in result
        assert 'world' in result
        assert '123' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withHerPonytail(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'her ponytail' ])
        assert result is not None
        assert len(result) == 2
        assert 'her ponytail' in result
        assert 'ponytail' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withHisCar(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'his car' ])
        assert result is not None
        assert len(result) == 2
        assert 'his car' in result
        assert 'car' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withKurtVonnegutJr(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '(Kurt) Vonnegut (Jr.)' ])
        assert result is not None
        assert len(result) == 4
        assert 'kurt vonnegut' in result
        assert 'kurt vonnegut jr' in result
        assert 'vonnegut' in result
        assert 'vonnegut jr' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withLuigiMarioJunior(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'Luigi M. Mario Jr.' ])
        assert result is not None
        assert len(result) == 4
        assert 'luigi m mario jr' in result
        assert 'luigi m mario' in result
        assert 'luigi mario jr' in result
        assert 'luigi mario' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withMarioMarioSenior(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'Mario M Mario Senior' ])
        assert result is not None
        assert len(result) == 4
        assert 'mario m mario senior' in result
        assert 'mario m mario' in result
        assert 'mario mario senior' in result
        assert 'mario mario' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withNone(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList(None)
        assert result is not None
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withNumberWord(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'three' ])
        assert result is not None
        assert len(result) == 1
        assert 'three' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withNumberWords(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'one', 'two' ])
        assert result is not None
        assert len(result) == 2
        assert 'one' in result
        assert 'two' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withOrdinalWord(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'third' ])
        assert result is not None
        assert len(result) == 1
        assert 'third' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withOrdinalWords(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'first', 'second' ])
        assert result is not None
        assert len(result) == 2
        assert 'first' in result
        assert 'second' in result

    @pytest.mark.asyncio
    async def test_expandNumerals_withSimpleDigit1(self):
        result: List[str] = await self.triviaAnswerCompiler.expandNumerals('3')
        assert result is not None
        assert len(result) == 3
        assert 'three' in result  # cardinal, year, individual digits
        assert 'third' in result  # ordinal
        assert 'the third' in result  # ordinal preceded by 'the'

    @pytest.mark.asyncio
    async def test_expandNumerals_withSimpleDigit2(self):
        result: List[str] = await self.triviaAnswerCompiler.expandNumerals('50')
        assert result is not None
        assert len(result) == 4
        assert 'fifty' in result  # cardinal, year, individual digits
        assert 'five zero' in result  # cardinal, year, individual digits
        assert 'fiftieth' in result  # ordinal
        assert 'the fiftieth' in result  # ordinal preceded by 'the'

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withTheirHouse(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'their house' ])
        assert result is not None
        assert len(result) == 2
        assert 'their house' in result
        assert 'house' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withTheyAreFriends(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'they are friends' ])
        assert result is not None
        assert len(result) == 2
        assert 'they are friends' in result
        assert 'friends' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withTheyreFriends(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'they\'re friends' ])
        assert result is not None
        assert len(result) == 2
        assert 'theyre friends' in result
        assert 'friends' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withUsDollar1(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '$12,456.70' ])
        assert result is not None
        assert len(result) == 2
        assert '1245670 usd' in result
        assert '1245670' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withUsDollar2(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '$123 USD' ])
        assert result is not None
        assert len(result) == 2
        assert '123 usd' in result
        assert '123' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withUsDollar3(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '$1 US' ])
        assert result is not None
        assert len(result) == 2
        assert '1 usd' in result
        assert '1' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withUsDollar4(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '$1000000000.55 USD' ])
        assert result is not None
        assert len(result) == 2
        assert '100000000055 usd' in result
        assert '100000000055' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withYourName(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ 'your name' ])
        assert result is not None
        assert len(result) == 2
        assert 'your name' in result
        assert 'name' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withYear(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '1 year' ])
        assert result is not None
        assert len(result) == 2
        assert '1 year' in result
        assert '1' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withYears(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '5 years' ])
        assert result is not None
        assert len(result) == 2
        assert '5 years' in result
        assert '5' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withYearOld(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '1 year old' ])
        assert result is not None
        assert len(result) == 2
        assert '1 year old' in result
        assert '1' in result

    @pytest.mark.asyncio
    async def test_compileTextAnswersList_withYearsOld(self):
        result: List[str] = await self.triviaAnswerCompiler.compileTextAnswersList([ '50 years old' ])
        assert result is not None
        assert len(result) == 2
        assert '50 years old' in result
        assert '50' in result

    @pytest.mark.asyncio
    async def test_expandNumerals_withYear1(self):
        result: List[str] = await self.triviaAnswerCompiler.expandNumerals('1234')
        assert result is not None
        assert len(result) == 5
        assert 'one thousand two hundred and thirty four' in result  # cardinal
        assert 'one thousand two hundred and thirty fourth' in result  # ordinal
        assert 'the one thousand two hundred and thirty fourth' in result  # ordinal preceded by 'the'
        assert 'twelve thirty four' in result  # year
        assert 'one two three four' in result  # individual digits

    @pytest.mark.asyncio
    async def test_expandNumerals_withRomanNumerals(self):
        result: List[str] = await self.triviaAnswerCompiler.expandNumerals('XIV')
        assert result is not None
        assert len(result) == 4
        assert 'fourteen' in result  # cardinal, year
        assert 'fourteenth' in result  # ordinal
        assert 'the fourteenth' in result  # ordinal preceded by 'the'
        assert 'xiv' in result

    def test_sanity(self):
        assert self.triviaAnswerCompiler is not None
        assert isinstance(self.triviaAnswerCompiler, TriviaAnswerCompiler)
