try:
    from ...trivia.bannedWords.bannedWord import BannedWord
    from ...trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
except:
    from trivia.bannedWords.bannedWord import BannedWord
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType


class TestBannedWord():

    def test_equals_withDifferentCheckTypes(self):
        one = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'hello'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'hello'
        )

        assert one != two

        one = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'HELLO'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'hello'
        )

        assert one != two

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

    def test_equals(self):
        one = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'zebra'
        )

        two = BannedWord(
            checkType = BannedWordCheckType.ANYWHERE,
            word = 'Zebra'
        )

        assert one == two

        three = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'zebra'
        )

        assert one != three
        assert two != three

    def test_isPhrase_withHello(self):
        bw = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'hello'
        )

        assert bw.getWord() == 'hello'
        assert len(bw.getWords()) == 1
        assert bw.getWords()[0] == 'hello'
        assert not bw.isPhrase()

    def test_isPhrase_withHelloWorld(self):
        bw = BannedWord(
            checkType = BannedWordCheckType.EXACT_MATCH,
            word = 'hello world'
        )

        assert bw.getWord() == 'hello world'
        assert len(bw.getWords()) == 2
        assert bw.getWords()[0] == 'hello'
        assert bw.getWords()[1] == 'world'
        assert bw.isPhrase()
