import pytest

try:
    from ...contentScanner.bannedPhrase import BannedPhrase
    from ...contentScanner.bannedWord import BannedWord
    from ...contentScanner.bannedWordsRepository import BannedWordsRepository
    from ...contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from ...contentScanner.contentCode import ContentCode
    from ...contentScanner.contentScanner import ContentScanner
    from ...contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from ...storage.linesReaderInterface import LinesReaderInterface
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
except:
    from contentScanner.bannedPhrase import BannedPhrase
    from contentScanner.bannedWord import BannedWord
    from contentScanner.bannedWordsRepository import BannedWordsRepository
    from contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScanner import ContentScanner
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from storage.linesReaderInterface import LinesReaderInterface
    from storage.linesStaticReader import LinesStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub


class TestContentScanner():

    timber: TimberInterface = TimberStub()

    bannedWordsRepository: BannedWordsRepository = BannedWordsRepository(
        bannedWordsLinesReader = LinesStaticReader(
            lines = [ 'Hello', 'WORLD', '"QAnon"', 'world' ]
        ),
        timber = timber
    )

    contentScanner: ContentScannerInterface = ContentScanner(
        bannedWordsRepository = bannedWordsRepository,
        timber = timber
    )

    @pytest.mark.asyncio
    async def test_scan_withBlankString(self):
        result = await self.contentScanner.scan(' ')
        assert result is ContentCode.IS_BLANK

    @pytest.mark.asyncio
    async def test_scan_withEmptyString(self):
        result = await self.contentScanner.scan('')
        assert result is ContentCode.IS_EMPTY

    @pytest.mark.asyncio
    async def test_scan_withNone(self):
        result = await self.contentScanner.scan(None)
        assert result is ContentCode.IS_NONE

    @pytest.mark.asyncio
    async def test_updatePhrasesContent(self):
        pass

    @pytest.mark.asyncio
    async def test_updateWordsContent(self):
        pass
