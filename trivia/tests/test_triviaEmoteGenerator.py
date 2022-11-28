import asyncio
from asyncio import AbstractEventLoop

import pytest

try:
    from ...storage.backingPsqlDatabase import BackingPsqlDatabase
    from ...storage.psqlCredentialsProvider import PsqlCredentialsProvider
    from ...trivia.triviaEmoteGenerator import TriviaEmoteGenerator
except:
    from storage.backingPsqlDatabase import BackingPsqlDatabase
    from storage.psqlCredentialsProvider import PsqlCredentialsProvider
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator


class TestTriviaEmoteGenerator():

    eventLoop: AbstractEventLoop = asyncio.get_event_loop()
    backingDatabase: BackingPsqlDatabase = BackingPsqlDatabase(
        eventLoop = eventLoop,
        psqlCredentialsProvider = PsqlCredentialsProvider()
    )
    triviaEmoteGenerator: TriviaEmoteGenerator = TriviaEmoteGenerator(
        backingDatabase = backingDatabase
    )

    @pytest.mark.asyncio
    async def test_getRandomEmote(self):
        for _ in range(100):
            result = self.triviaEmoteGenerator.getRandomEmote()
            assert result is not None
            assert isinstance(result, str)
            assert not result.isspace()
            assert len(result) >= 1
            assert result == await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(result)

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAbacus(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧮')
        assert result is not None
        assert result == '🧮'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAlembic(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('⚗️')
        assert result is not None
        assert result == '⚗️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAlien(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👽')
        assert result is not None
        assert result == '👽'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBackpack(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🎒')
        assert result is not None
        assert result == '🎒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBarChart(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📊')
        assert result is not None
        assert result == '📊'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBanana(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍌')
        assert result is not None
        assert result == '🍌'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBlueberry(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🫐')
        assert result is not None
        assert result == '🫐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCardIndex(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📇')
        assert result is not None
        assert result == '📇'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCarrot(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🥕')
        assert result is not None
        assert result == '🥕'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCheese(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧀')
        assert result is not None
        assert result == '🧀'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCherry(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍒')
        assert result is not None
        assert result == '🍒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withClipboard(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📋')
        assert result is not None
        assert result == '📋'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCrab(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🦀')
        assert result is not None
        assert result == '🦀'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCrayon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🖍️')
        assert result is not None
        assert result == '🖍️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCurryRice(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍛')
        assert result is not None
        assert result == '🍛'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDolphin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐬')
        assert result is not None
        assert result == '🐬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDna(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧬')
        assert result is not None
        assert result == '🧬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withEmptyString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('')
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withFaceWithMonocle(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧐')
        assert result is not None
        assert result == '🧐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withFireTruck(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🚒')
        assert result is not None
        assert result == '🚒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withGrapes(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍇')
        assert result is not None
        assert result == '🍇'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withGreenApple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍏')
        assert result is not None
        assert result == '🍏'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withHelicopter(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🚁')
        assert result is not None
        assert result == '🚁'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withLedger(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📒')
        assert result is not None
        assert result == '📒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withLightBulb(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('💡')
        assert result is not None
        assert result == '💡'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMelon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍈')
        assert result is not None
        assert result == '🍈'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMicroscope(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🔬')
        assert result is not None
        assert result == '🔬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withMushroom(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍄')
        assert result is not None
        assert result == '🍄'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNerdFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🤓')
        assert result is not None
        assert result == '🤓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNewLineString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('\n')
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNone(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNotebook(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📓')
        assert result is not None
        assert result == '📓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPaperclip(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📎')
        assert result is not None
        assert result == '📎'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPencil(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('✏️')
        assert result is not None
        assert result == '✏️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPenguin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐧')
        assert result is not None
        assert result == '🐧'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPineapple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍍')
        assert result is not None
        assert result == '🍍'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPotato(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🥔')
        assert result is not None
        assert result == '🥔'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRedApple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍎')
        assert result is not None
        assert result == '🍎'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRoastedSweetPotato(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍠')
        assert result is not None
        assert result == '🍠'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRocket(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🚀')
        assert result is not None
        assert result == '🚀'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withSchool(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🏫')
        assert result is not None
        assert result == '🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withShrimp(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🦐')
        assert result is not None
        assert result == '🦐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStraightRuler(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📏')
        assert result is not None
        assert result == '📏'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStrawberry(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍓')
        assert result is not None
        assert result == '🍓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTangerine(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍊')
        assert result is not None
        assert result == '🍊'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTelescope(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🔭')
        assert result is not None
        assert result == '🔭'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withThinkingFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🤔')
        assert result is not None
        assert result == '🤔'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withThoughtBalloon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('💭')
        assert result is not None
        assert result == '💭'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTomato(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍅')
        assert result is not None
        assert result == '🍅'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTriangularRuler(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📐')
        assert result is not None
        assert result == '📐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWatermelon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍉')
        assert result is not None
        assert result == '🍉'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTulip(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🌷')
        assert result is not None
        assert result == '🌷'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWhale(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🐋')
        assert result is not None
        assert result == '🐋'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWhitespaceString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(' ')
        assert result is None

    def test_sanity(self):
        assert self.triviaEmoteGenerator is not None
        assert isinstance(self.triviaEmoteGenerator, TriviaEmoteGenerator)
