import pytest

try:
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ..bannedWordsRepository import BannedWordsRepository
    from ..bannedWordsRepositoryInterface import BannedWordsRepositoryInterface
    from ..contentCode import ContentCode
    from ..contentScanner import ContentScanner
    from ..contentScannerInterface import ContentScannerInterface
except:
    from contentScanner.bannedWordsRepository import BannedWordsRepository
    from contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScanner import ContentScanner
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from storage.linesStaticReader import LinesStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub


class TestContentScanner():

    timber: TimberInterface = TimberStub()

    bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
        bannedWordsLinesReader = LinesStaticReader(
            lines = [ 'Nintendo', 'SONY', '"QAnon"', 'sony' ]
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
    async def test_scan_withHelloWorld(self):
        result = await self.contentScanner.scan('Hello, World!')
        assert result is ContentCode.OK

    @pytest.mark.asyncio
    async def test_scan_withNone(self):
        result = await self.contentScanner.scan(None)
        assert result is ContentCode.IS_NONE

    @pytest.mark.asyncio
    async def test_scan_withUrl(self):
        result = await self.contentScanner.scan('Hello https://google.com/ World!')
        assert result is ContentCode.OK

    @pytest.mark.asyncio
    async def test_updatePhrasesContent(self):
        pass

    @pytest.mark.asyncio
    async def test_updateWordsContent(self):
        pass
