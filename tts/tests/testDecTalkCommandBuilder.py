import pytest

try:
    from ..decTalkCommandBuilder import DecTalkCommandBuilder
    from ..ttsCommandBuilderInterface import TtsCommandBuilderInterface
except:
    from tts.decTalkCommandBuilder import DecTalkCommandBuilder
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface


class DecTalkCommandBuilderTests():

    decTalkCommandBuilder: TtsCommandBuilderInterface = DecTalkCommandBuilder(
        pathToDecTalk = 'say.exe'
    )

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withEmptyString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDangerousCharactersString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('& cd C:\\ & dir')
        assert result == 'say.exe cd C:\\ dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString1(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-post hello')
        assert result == 'say.exe hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString2(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-pre hello')
        assert result == 'say.exe hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString3(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-l hello')
        assert result == 'say.exe hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString4(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-lw hello')
        assert result == 'say.exe hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDecTalkFlagsString5(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('-l[t] hello')
        assert result == 'say.exe hello'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withDirectoryTraversalString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('& cd .. & dir')
        assert result == 'say.exe cd dir'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withHelloWorldString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand('Hello, World!')
        assert result == 'say.exe Hello, World!'

    @pytest.mark.asyncio
    async def test_buildAndCleanCommand_withNone(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand(None)
        assert result is None

    @pytest
    async def test_buildAndCleanCommand_withWhitespaceString(self):
        result = await self.decTalkCommandBuilder.buildAndCleanCommand(' ')
        assert result is None
