from typing import List

try:
    from ...trivia.triviaDifficulty import TriviaDifficulty
except:
    from trivia.triviaDifficulty import TriviaDifficulty


class TestTriviaDifficulty():

    def test_fromStr_withEmptyString(self):
        result: TriviaDifficulty = None
        exception: Exception = None

        try:
            result = TriviaDifficulty.fromStr('')
        except Exception as e:
            exception = e

        assert result is TriviaDifficulty.UNKNOWN
        assert exception is None

    def test_fromStr_withEasyString(self):
        result = TriviaDifficulty.fromStr('easy')
        assert result is TriviaDifficulty.EASY

    def test_fromStr_withHardString(self):
        result = TriviaDifficulty.fromStr('hard')
        assert result is TriviaDifficulty.HARD

    def test_fromStr_withMediumString(self):
        result = TriviaDifficulty.fromStr('medium')
        assert result is TriviaDifficulty.MEDIUM

    def test_fromStr_withNone(self):
        result: TriviaDifficulty = None
        exception: Exception = None

        try:
            result = TriviaDifficulty.fromStr(None)
        except Exception as e:
            exception = e

        assert result is TriviaDifficulty.UNKNOWN
        assert exception is None

    def test_fromStr_withWhitespaceString(self):
        result: TriviaDifficulty = None
        exception: Exception = None

        try:
            result = TriviaDifficulty.fromStr(' ')
        except Exception as e:
            exception = e

        assert result is TriviaDifficulty.UNKNOWN
        assert exception is None

    def test_toInt_withEasy(self):
        result = TriviaDifficulty.EASY.toInt()
        assert result == 1

    def test_toInt_withHard(self):
        result = TriviaDifficulty.HARD.toInt()
        assert result == 3

    def test_toInt_withMedium(self):
        result = TriviaDifficulty.MEDIUM.toInt()
        assert result == 2

    def test_toInt_withUnknown(self):
        result = TriviaDifficulty.UNKNOWN.toInt()
        assert result == 0

    def test_toStr_withEasy(self):
        result = TriviaDifficulty.EASY.toStr()
        assert result == 'easy'

    def test_toStr_withHard(self):
        result = TriviaDifficulty.HARD.toStr()
        assert result == 'hard'

    def test_toStr_withMedium(self):
        result = TriviaDifficulty.MEDIUM.toStr()
        assert result == 'medium'

    def test_toStr_withUnkown(self):
        result = TriviaDifficulty.UNKNOWN.toStr()
        assert result == 'unknown'
