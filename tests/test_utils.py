try:
    import CynanBotCommon.utils as utils
except:
    import utils


class UtilsTest():

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
