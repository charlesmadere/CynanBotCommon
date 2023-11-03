import pytest

try:
    from ...contentScanner.bannedWordsRepository import BannedWordsRepository
    from ...contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from ...contentScanner.contentScanner import ContentScanner
    from ...contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from ...storage.jsonStaticReader import JsonStaticReader
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ...tts.ttsSettingsRepository import TtsSettingsRepository
    from ...tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from ..decTalkCommandBuilder import DecTalkCommandBuilder
    from ..ttsCommandBuilderInterface import TtsCommandBuilderInterface
except:
    from contentScanner.bannedWordsRepository import BannedWordsRepository
    from contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from contentScanner.contentScanner import ContentScanner
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from storage.jsonStaticReader import JsonStaticReader
    from storage.linesStaticReader import LinesStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub
    from tts.decTalkCommandBuilder import DecTalkCommandBuilder
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface
    from tts.ttsSettingsRepository import TtsSettingsRepository
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface


class TestDecTalkCommandBuilder():

    timber: TimberInterface = TimberStub()

    bannedWordsRepository: BannedWordsRepositoryInterface = BannedWordsRepository(
        bannedWordsLinesReader = LinesStaticReader(
            lines = [ 'hydroxychloroquine' ]
        ),
        timber = timber
    )

    contentScanner: ContentScannerInterface = ContentScanner(
        bannedWordsRepository = bannedWordsRepository,
        timber = timber
    )

    ttsSettingsRepository: TtsSettingsRepositoryInterface = TtsSettingsRepository(
        settingsJsonReader = JsonStaticReader(
            jsonContents = {
                'isEnabled': True
            }
        )
    )

    decTalkCommandBuilder: TtsCommandBuilderInterface = DecTalkCommandBuilder(
        contentScanner = contentScanner,
        timber = timber,
        ttsSettingsRepository = ttsSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withEmptyString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withBannedWord(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('have you tried hydroxychloroquine?')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDangerousCharactersString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('& cd C:\\ & dir')
        assert result == 'cd C:\\ dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString1(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-post hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString2(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-pre hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString3(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-l hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString4(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-lw hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString5(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-l[t] hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString6(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-v show version information')
        assert result == 'show version information'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString7(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-d userDict')
        assert result == 'userDict'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString8(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-lang uk hello world')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDirectoryTraversalString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('& cd .. & dir')
        assert result == 'cd dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withExtraneousSpacesString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('  Hello,    World! ')
        assert result == 'Hello, World!'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withHelloWorldString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('Hello, World!')
        assert result == 'Hello, World!'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withNone(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withWhitespaceString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand(' ')
        assert result is None
