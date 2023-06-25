try:
    from ...trivia.bannedWords.bannedWord import BannedWord
    from ...trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
except:
    from trivia.bannedWords.bannedWord import BannedWord
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType


class TestBannedWord():

    def test_equals_withDifferentWords(self):
        one = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'cat'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'dog'
        )

        assert one != two

        one = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'cat'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'dog'
        )

        assert one != two

        one = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'cat'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'dog'
        )

        assert one != two

    def test_equals_withDifferentCheckTypes(self):
        one = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'hello'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'hello'
        )

        assert one == two

        one = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'HELLO'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'hello'
        )

        assert one == two