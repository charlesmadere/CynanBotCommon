import math
from typing import List

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TestUtils():

    def test_areAllStrsInts_withEmptyList(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.areAllStrsInts(list())
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, Exception)

    def test_areAllStrsInts_withIntList(self):
        result = utils.areAllStrsInts([ '1', '10', '100', '1000' ])
        assert result is True

    def test_areAllStrsInts_withMixedList(self):
        result = utils.areAllStrsInts([ '1', '10', '100', 'hello', '1000', 'world' ])
        assert result is False

    def test_areAllStrsInts_withNone(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.areAllStrsInts(None)
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, Exception)

    def test_areAllStrsInts_withWordList(self):
        result = utils.areAllStrsInts([ 'hello', 'world' ])
        assert result is False

    def test_containsUrl_withEmptyString(self):
        result = utils.containsUrl('')
        assert result is False

    def test_containsUrl_withGoogle(self):
        result = utils.containsUrl('https://www.google.com/')
        assert result is True

    def test_containsUrl_withGoogleSentence(self):
        result = utils.containsUrl('There\'s a URL here: https://www.google.com/ in this sentence.')
        assert result is True

    def test_containsUrl_withNone(self):
        result = utils.containsUrl(None)
        assert result is False

    def test_containsUrl_withRandomNoise1(self):
        result = utils.containsUrl('Qd19u(KAyCuZ~qNQkd-iy\\%\\E|KxRc')
        assert result is False

    def test_containsUrl_withRandomNoise2(self):
        result = utils.containsUrl('.s*&Sxwa}RZ\\\'AIkvD6:&OkVT#_YA`')
        assert result is False

    def test_copyList_withEmptyList(self):
        original: List = list()
        result: List = utils.copyList(original)
        assert result is not None
        assert len(result) == 0
        assert result is not original

    def test_copyList_withIntList(self):
        original: List[int] = [ 1, 2, 3, 4 ]
        result: List = utils.copyList(original)
        assert result is not None
        assert len(result) == 4
        assert result is not original
        assert result == original

    def test_copyList_withNone(self):
        result: List = utils.copyList(None)
        assert result is not None
        assert len(result) == 0

    def test_copyList_withStrList(self):
        original: List[str] = [ '1', '2', '3', '4' ]
        result: List = utils.copyList(original)
        assert result is not None
        assert len(result) == 4
        assert result is not original
        assert result == original

    def test_getCleanedSplits_withEmptyString(self):
        original: str = ''
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 0

    def test_getCleanedSplits_withHelloWorld(self):
        original: str = 'Hello, World!'
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 2
        assert result[0] == 'Hello,'
        assert result[1] == 'World!'

    def test_getCleanedSplits_withNone(self):
        original: str = None
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 0

    def test_getCleanedSplits_withWhitespaceString(self):
        original: str = ' '
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 0

    def test_isValidBool_withFalse(self):
        result: bool = utils.isValidBool(False)
        assert result is True

    def test_isValidBool_withNone(self):
        result: bool = utils.isValidBool(None)
        assert result is False

    def test_isValidBool_withTrue(self):
        result: bool = utils.isValidBool(True)
        assert result is True

    def test_isValidInt_withNan(self):
        result: bool = utils.isValidInt(math.nan)
        assert result is False

    def test_isValidInt_withNegativeOne(self):
        result: bool = utils.isValidInt(-1)
        assert result is True

    def test_isValidInt_withNone(self):
        result: bool = utils.isValidInt(None)
        assert result is False

    def test_isValidInt_withOne(self):
        result: bool = utils.isValidInt(1)
        assert result is True

    def test_isValidInt_withPi(self):
        result: bool = utils.isValidInt(math.pi)
        assert result is False

    def test_isValidInt_withTwo(self):
        result: bool = utils.isValidInt(2)
        assert result is True

    def test_isValidInt_withZero(self):
        result: bool = utils.isValidInt(0)
        assert result is True

    def test_isValidNum_withFloat(self):
        result: bool = utils.isValidNum(3.14)
        assert result is True

    def test_isValidNum_withInt(self):
        result: bool = utils.isValidNum(100)
        assert result is True

    def test_isValidNum_withNan(self):
        result: bool = utils.isValidNum(math.nan)
        assert result is False

    def test_isValidNum_withNone(self):
        result: bool = utils.isValidNum(None)
        assert result is False

    def test_isValidStr_withEmptyString(self):
        result: bool = utils.isValidStr('')
        assert result is False

    def test_isValidStr_withHelloWorldString(self):
        result: bool = utils.isValidStr('Hello, World!')
        assert result is True

    def test_isValidStr_withNewLineString(self):
        result: bool = utils.isValidStr('\n')
        assert result is False

    def test_isValidStr_withNone(self):
        result: bool = utils.isValidStr(None)
        assert result is False

    def test_isValidStr_withWhitespaceString(self):
        result: bool = utils.isValidStr(' ')
        assert result is False

    def test_isValidUrl_withEmptyString(self):
        result = utils.isValidUrl('')
        assert result is False

    def test_isValidUrl_withGoogle(self):
        result = utils.isValidUrl('https://www.google.com/')
        assert result is True

        result = utils.isValidUrl('http://google.com')
        assert result is True

        result = utils.isValidUrl('https://google.com:8080/')
        assert result is True

    def test_isValidUrl_withNone(self):
        result = utils.isValidUrl(None)
        assert result is False

    def test_isValidUrl_withRandomNoise1(self):
        result = utils.isValidUrl('J)R+ALY,m`g9r>lO`+RMeb$XL.OF8np')
        assert result is False

    def test_isValidUrl_withRandomNoise2(self):
        result = utils.isValidUrl('rpt\\\'%TmN$lx!T.Gg2le)QVO4\\_UqMA8dA{=\\\'\\\"')
        assert result is False

    def test_isValidUrl_withWhitespaceString(self):
        result = utils.isValidUrl(' ')
        assert result is False

    def test_strictStrToBool_withEmptyString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool('')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strictStrToBool_withF(self):
        result: bool = utils.strictStrToBool('f')
        assert result is False

    def test_strictStrToBool_withFalse(self):
        result: bool = utils.strictStrToBool('false')
        assert result is False

    def test_strictStrToBool_withNewLineString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool('\n')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strictStrToBool_withNone(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool(None)
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strictStrToBool_withT(self):
        result: bool = utils.strictStrToBool('t')
        assert result is True

    def test_strictStrToBool_withTrue(self):
        result: bool = utils.strictStrToBool('true')
        assert result is True

    def test_strictStrToBool_withWhitespaceString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool(' ')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strToBool_withEmptyString(self):
        result: bool = utils.strToBool('')
        assert result is True

    def test_strToBool_withF(self):
        result: bool = utils.strToBool('f')
        assert result is False

    def test_strToBool_withFalse(self):
        result: bool = utils.strToBool('false')
        assert result is False

    def test_strToBool_withNewLineString(self):
        result: bool = utils.strToBool('\n')
        assert result is True

    def test_strToBool_withNone(self):
        result: bool = utils.strToBool(None)
        assert result is True

    def test_strToBool_withT(self):
        result: bool = utils.strToBool('t')
        assert result is True

    def test_strToBool_withTrue(self):
        result: bool = utils.strToBool('true')
        assert result is True

    def test_strToBool_withWhitespaceString(self):
        result: bool = utils.strToBool(' ')
        assert result is True
