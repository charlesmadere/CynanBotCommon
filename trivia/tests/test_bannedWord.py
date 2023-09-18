try:
    from ...trivia.bannedWords.bannedWord import BannedWord
except:
    from trivia.bannedWords.bannedWord import BannedWord


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
