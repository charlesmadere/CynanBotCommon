from typing import List

import pytest

try:
    from ...storage.jsonStaticReader import JsonStaticReader
    from ...storage.linesReaderInterface import LinesReaderInterface
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ...trivia.absTriviaQuestion import AbsTriviaQuestion
    from ...trivia.bannedWords.bannedWordsRepository import \
        BannedWordsRepository
    from ...trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from ...trivia.triviaContentCode import TriviaContentCode
    from ...trivia.triviaContentScanner import TriviaContentScanner
    from ...trivia.triviaDifficulty import TriviaDifficulty
    from ...trivia.triviaSettingsRepository import TriviaSettingsRepository
    from ...trivia.triviaSource import TriviaSource
    from ...trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion
except:
    from storage.jsonStaticReader import JsonStaticReader
    from storage.linesReaderInterface import LinesReaderInterface
    from storage.linesStaticReader import LinesStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.bannedWords.bannedWordsRepository import BannedWordsRepository
    from trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TestTriviaContentScanner():

    triviaSettingsRepository = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(jsonContents = dict())
    )

    bannedWordsLinesReader: LinesReaderInterface = LinesStaticReader(
        lines = [ 'bitch', '"trump"' ],
    )

    timber: TimberInterface = TimberStub()

    bannedWordsRepositoryInterface: BannedWordsRepositoryInterface = BannedWordsRepository(
        bannedWordsLinesReader = bannedWordsLinesReader,
        timber = timber
    )

    triviaContentScanner = TriviaContentScanner(
        bannedWordsRepositoryInterface = bannedWordsRepositoryInterface,
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_verify_withNone(self):
        result = await self.triviaContentScanner.verify(None)
        assert result is TriviaContentCode.IS_NONE

    @pytest.mark.asyncio
    async def test_verify_withSimpleTriviaQuestion1(self):
        correctAnswers: List[bool] = list()
        correctAnswers.append(True)

        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = correctAnswers,
            category = None,
            categoryId = None,
            question = 'What is?',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.TRIVIA_DATABASE
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.OK

    @pytest.mark.asyncio
    async def test_verify_withSimpleTriviaQuestion2(self):
        correctAnswers: List[bool] = list()
        correctAnswers.append(False)

        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = correctAnswers,
            category = None,
            categoryId = None,
            question = 'Blah blah question here?',
            triviaId = 'abc456',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.J_SERVICE
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.OK
