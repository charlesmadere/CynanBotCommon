import asyncio
from asyncio import AbstractEventLoop

import pytest

try:
    from ...backgroundTaskHelper import BackgroundTaskHelper
    from ...storage.linesReaderInterface import LinesReaderInterface
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timber import Timber
    from ...trivia.bannedWords.bannedWord import BannedWord
    from ...trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
    from ...trivia.bannedWords.bannedWordsRepository import \
        BannedWordsRepository
    from ...trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
except:
    from backgroundTaskHelper import BackgroundTaskHelper
    from storage.linesReaderInterface import LinesReaderInterface
    from storage.linesStaticReader import LinesStaticReader
    from timber.timber import Timber
    from trivia.bannedWords.bannedWord import BannedWord
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
    from trivia.bannedWords.bannedWordsRepository import BannedWordsRepository
    from trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface


class TestBannedWordsRepository():

    eventLoop: AbstractEventLoop = asyncio.get_event_loop()
    backgroundTaskHelper = BackgroundTaskHelper(eventLoop = eventLoop)
    timber = Timber(backgroundTaskHelper = backgroundTaskHelper)

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

        assert BannedWord(BannedWordCheckType.ANYWHERE, 'hello') in bannedWords
        assert BannedWord(BannedWordCheckType.ANYWHERE, 'world') in bannedWords
        assert BannedWord(BannedWordCheckType.EXACT_MATCH, 'qanon') in bannedWords

    @pytest.mark.asyncio
    async def test_getBannedWordsAsync(self):
        bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
            bannedWordsLinesReader = self.bannedWordsLinesReader,
            timber = self.timber
        )

        bannedWords = await bannedWordsRepository.getBannedWordsAsync()
        assert len(bannedWords) == 3

        assert BannedWord(BannedWordCheckType.ANYWHERE, 'hello') in bannedWords
        assert BannedWord(BannedWordCheckType.ANYWHERE, 'world') in bannedWords
        assert BannedWord(BannedWordCheckType.EXACT_MATCH, 'qanon') in bannedWords

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
