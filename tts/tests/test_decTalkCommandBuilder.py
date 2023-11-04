import pytest

try:
    from ...contentScanner.bannedWordsRepository import BannedWordsRepository
    from ...contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from ...contentScanner.contentScanner import ContentScanner
    from ...contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from ...emojiHelper.emojiHelper import EmojiHelper
    from ...emojiHelper.emojiHelperInterface import EmojiHelperInterface
    from ...emojiHelper.emojiRepository import EmojiRepository
    from ...emojiHelper.emojiRepositoryInterface import \
        EmojiRepositoryInterface
    from ...storage.jsonFileReader import JsonFileReader
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
    from emojiHelper.emojiHelper import EmojiHelper
    from emojiHelper.emojiHelperInterface import EmojiHelperInterface
    from emojiHelper.emojiRepository import EmojiRepository
    from emojiHelper.emojiRepositoryInterface import EmojiRepositoryInterface
    from storage.jsonFileReader import JsonFileReader
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

    emojiRepository: EmojiRepositoryInterface = EmojiRepository(
        emojiJsonReader = JsonFileReader('emojiHelper/emojiRepository.json'),
        timber = timber
    )

    emojiHelper: EmojiHelperInterface = EmojiHelper(
        emojiRepository = emojiRepository
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
        emojiHelper = emojiHelper,
        timber = timber,
        ttsSettingsRepository = ttsSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withEmptyString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withBannedWord(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('have you tried hydroxychloroquine?')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDangerousCharactersString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('& cd C:\\ & dir')
        assert result == 'cd C:\\ dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString1(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-post hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString2(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-pre hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString3(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-l hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString4(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-lw hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString5(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-l[t] hello')
        assert result == 'hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString6(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-v show version information')
        assert result == 'show version information'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString7(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-d userDict')
        assert result == 'userDict'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDecTalkFlagsString8(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('-lang uk hello world')
        assert result == 'hello world'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withDirectoryTraversalString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('& cd .. & dir')
        assert result == 'cd dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withExtraneousSpacesString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('  Hello,    World! ')
        assert result == 'Hello, World!'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withHelloWorldString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage('Hello, World!')
        assert result == 'Hello, World!'

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withNone(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanMessage_withWhitespaceString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanMessage(' ')
        assert result is None
