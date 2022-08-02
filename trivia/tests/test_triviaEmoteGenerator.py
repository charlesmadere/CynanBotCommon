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
        for _ in 100:
            result = self.triviaEmoteGenerator.getRandomEmote()
            assert result is not None
            assert isinstance(result, str)
            assert not result.isspace()
            assert len(result) >= 1
            assert emoji.is_emoji(result)

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withEmptyString(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('')
        assert result is None

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withManStudent(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '👨‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withManStudentDarkSkin(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨🏿‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '👨‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withManStudentLightSkin(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👨🏻‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '👨‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withNewLineString(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('\n')
        assert result is None

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withNone(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(None)
        assert result is None

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withSchool(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🏫')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🏫'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withStudent(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withStudentDarkSkin(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑🏿‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withStudentLightSkin(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('🧑🏻‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '🧑‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withWhitespaceString(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote(' ')
        assert result is None

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withWomanStudent(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '👩‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withWomanStudentDarkSkin(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩🏿‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '👩‍🎓'

    @pytest.mark.asyncio
    def test_getValidatedAndNormalizedEmote_withWomanStudentLightSkin(self):
        result = self.triviaEmoteGenerator.getValidatedAndNormalizedEmote('👩🏻‍🎓')
        assert result is not None
        assert emoji.is_emoji(result)
        assert result == '👩‍🎓'

    def test_sanity(self):
        assert self.triviaEmoteGenerator is not None
        assert isinstance(self.triviaEmoteGenerator, TriviaEmoteGenerator)
