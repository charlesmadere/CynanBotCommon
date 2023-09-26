try:
    from ...trivia.bannedWords.bannedWord import BannedWord
    from ...trivia.bannedWords.bannedWordType import BannedWordType
except:
    from trivia.bannedWords.bannedWord import BannedWord
    from trivia.bannedWords.bannedWordType import BannedWordType


class TestBannedWord():

    def test_equals_withDifferentWords(self):
        one = BannedWord('cat')
        two = BannedWord('dog')
        assert one != two

    def test_equals_withSameWords(self):
        one = BannedWord('hello')
        two = BannedWord('hello')
        assert one == two

    def test_hash_withDifferentWords(self):
        one = BannedWord('cat')
        two = BannedWord('dog')
        assert hash(one) != hash(two)

    def test_hash_withSameWords(self):
        one = BannedWord('hello')
        two = BannedWord('hello')
        assert hash(one) == hash(two)

    def test_getType(self):
        word = BannedWord('hello')
        assert word.getType() is BannedWordType.EXACT_WORD
