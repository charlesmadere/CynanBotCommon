try:
    from ...trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
except:
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType


class TestBannedWordCheckType():

    def test_fromStr_withAnywhere(self):
        result = BannedWordCheckType.fromStr('anywhere')
        assert result is BannedWordCheckType.ANYWHERE

    def test_fromStr_withEmptyString(self):
        result: BannedWordCheckType = None
        exception: Exception = None

        try:
            result = BannedWordCheckType.fromStr('')
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, ValueError)

    def test_fromStr_withExactMatch(self):
        result = BannedWordCheckType.fromStr('exact_match')
        assert result is BannedWordCheckType.EXACT_MATCH

    def test_fromStr_withNone(self):
        result: BannedWordCheckType = None
        exception: Exception = None

        try:
            result = BannedWordCheckType.fromStr(None)
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, ValueError)

    def test_fromStr_withWhitespaceString(self):
        result: BannedWordCheckType = None
        exception: Exception = None

        try:
            result = BannedWordCheckType.fromStr(' ')
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, ValueError)
