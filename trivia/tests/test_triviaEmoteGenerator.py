import emoji
import pytest

try:
    from ...backingDatabase import BackingDatabase
    from ...trivia.triviaEmoteGenerator import TriviaEmoteGenerator
except:
    from backingDatabase import BackingDatabase
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator


class TestTriviaEmoteGenerator():

    triviaEmoteGenerator: TriviaEmoteGenerator = TriviaEmoteGenerator(BackingDatabase())

    def test_getRandomEmote(self):
        for _ in range(100):
            result = self.triviaEmoteGenerator.getRandomEmote()
            assert result is not None
            assert isinstance(result, str)
            assert not result.isspace()
            assert len(result) >= 1
            assert emoji.is_emoji(result)

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAbacus(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧮')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧮'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withAlien(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👽')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '👽'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBackpack(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🎒')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🎒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withBanana(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍌')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🍌'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withCrayon(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🖍️')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🖍️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withDna(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧬')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withEmptyString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('')
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withFaceWithMonocle(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧐')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withGreenApple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍏')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🍏'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withHealthWorker(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑‍⚕️')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍⚕️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withLedger(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📒')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '📒'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withManStudent(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withManStudentDarkSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨🏿‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withManStudentLightSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨🏻‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withManTeacher(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withManTeacherDarkSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨🏻‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withManTeacherLightSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨🏿‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withNerdFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🤓')
        assert result is not None
        assert emoji.is_emoji(result)
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
    async def test_getValidatedAndNormalizedEmote_withPencil(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📎')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '📎'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withPencil(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('✏️')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '✏️'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withRedApple(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🍎')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🍎'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withSchool(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withScientist(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑‍🔬')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🔬'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStraightRuler(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📏')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '📏'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStudent(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStudentDarkSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑🏿‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withStudentLightSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑🏻‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTeacher(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTeacherDarkSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑🏿‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTeacherLightSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑🏻‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTechnologist(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑‍💻')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍💻'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withThinkingFace(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🤔')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🤔'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withTriangularRuler(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('📐')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '📐'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWhitespaceString(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(' ')
        assert result is None

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWomanStudent(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWomanStudentDarkSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩🏿‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWomanStudentLightSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩🏻‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWomanTeacher(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWomanTeacherDarkSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩🏻‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    @pytest.mark.asyncio
    async def test_getValidatedAndNormalizedEmote_withWomanTeacherLightSkin(self):
        result = await self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩🏿‍🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🏫'

    def test_sanity(self):
        assert self.triviaEmoteGenerator is not None
        assert isinstance(self.triviaEmoteGenerator, TriviaEmoteGenerator)
