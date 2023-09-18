import pytest

try:
    from ...storage.linesReaderInterface import LinesReaderInterface
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ...trivia.bannedWords.bannedPhrase import BannedPhrase
    from ...trivia.bannedWords.bannedWord import BannedWord
    from ...trivia.bannedWords.bannedWordsRepository import \
        BannedWordsRepository
    from ...trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
except:
    from storage.linesReaderInterface import LinesReaderInterface
    from storage.linesStaticReader import LinesStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub
    from trivia.bannedWords.bannedPhrase import BannedPhrase
    from trivia.bannedWords.bannedWord import BannedWord
    from trivia.bannedWords.bannedWordsRepository import BannedWordsRepository
    from trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface


class TestBannedWordsRepository():

    timber: TimberInterface = TimberStub()

    bannedWordsLinesReader: LinesReaderInterface = LinesStaticReader(
        lines = [ 'Hello', 'WORLD', '"QAnon"' ]
    )

    emptyBannedWordsLinesReader: LinesReaderInterface = LinesStaticReader(
        lines = None
    )

    def test_getBannedWords(self):
        bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
            bannedWordsLinesReader = self.bannedWordsLinesReader,
            timber = self.timber
        )

        bannedWords = bannedWordsRepository.getBannedWords()
        assert len(bannedWords) == 3

        assert BannedWord('hello') in bannedWords
        assert BannedWord('world') in bannedWords
        assert BannedPhrase('qanon') in bannedWords

    @pytest.mark.asyncio
    async def test_getBannedWordsAsync(self):
        bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
            bannedWordsLinesReader = self.bannedWordsLinesReader,
            timber = self.timber
        )

        bannedWords = await bannedWordsRepository.getBannedWordsAsync()
        assert len(bannedWords) == 3

        assert BannedWord('hello') in bannedWords
        assert BannedWord('world') in bannedWords
        assert BannedPhrase('qanon') in bannedWords

    def test_getBannedWords_withEmptyBannedWordsLinesReader(self):
        bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
            bannedWordsLinesReader = self.emptyBannedWordsLinesReader,
            timber = self.timber
        )

        bannedWords = bannedWordsRepository.getBannedWords()
        assert len(bannedWords) == 0

    @pytest.mark.asyncio
    async def test_getBannedWordsAsync_withEmptyBannedWordsLinesReader(self):
        bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
            bannedWordsLinesReader = self.emptyBannedWordsLinesReader,
            timber = self.timber
        )

        bannedWords = await bannedWordsRepository.getBannedWordsAsync()
        assert len(bannedWords) == 0
