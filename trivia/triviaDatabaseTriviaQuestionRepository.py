from typing import Any, Dict, List

import aiosqlite

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class TriviaDatabaseTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaEmoteGenerator: TriviaEmoteGenerator,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaDatabaseFile: str = 'CynanBotCommon/trivia/triviaDatabaseTriviaQuestionRepository.sqlite'
    ):
        super().__init__(triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaEmoteGenerator is None:
            raise ValueError(f'triviaEmoteGenerator argument is malformed: \"{triviaEmoteGenerator}\"')
        elif triviaQuestionCompiler is None:
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')
        elif not utils.isValidStr(triviaDatabaseFile):
            raise ValueError(f'triviaDatabaseFile argument is malformed: \"{triviaDatabaseFile}\"')

        self.__timber: Timber = timber
        self.__triviaEmoteGenerator: TriviaEmoteGenerator = triviaEmoteGenerator
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler
        self.__triviaDatabaseFile: str = triviaDatabaseFile

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        self.__timber.log('TriviaDatabaseTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        triviaDict = await self.__fetchTriviaQuestionDict()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('TriviaDatabaseTriviaQuestionRepository', f'{triviaDict}')

        triviaId = utils.getStrFromDict(triviaDict, 'triviaId')

        category = utils.getStrFromDict(triviaDict, 'category')
        category = await self.__triviaQuestionCompiler.compileCategory(category)

        question = utils.getStrFromDict(triviaDict, 'question')
        question = await self.__triviaQuestionCompiler.compileQuestion(question)

        correctAnswer = utils.getStrFromDict(triviaDict, 'correctAnswer')
        correctAnswer = await self.__triviaQuestionCompiler.compileResponse(correctAnswer)

        correctAnswers: List[str] = list()
        correctAnswers.append(correctAnswer)

        wrongAnswers = await self.__triviaQuestionCompiler.compileResponses(triviaDict['wrongAnswers'])

        multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = wrongAnswers
        )

        triviaDifficultyInt = utils.getIntFromDict(triviaDict, 'difficulty', -1)
        triviaDifficulty = TriviaDifficulty.fromInt(triviaDifficultyInt)

        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)

        return MultipleChoiceTriviaQuestion(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = multipleChoiceResponses,
            category = category,
            categoryId = None,
            emote = emote,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = triviaDifficulty,
            triviaSource = TriviaSource.TRIVIA_DATABASE
        )

    async def __fetchTriviaQuestionDict(self) -> Dict[str, Any]:
        connection = await aiosqlite.connect(self.__triviaDatabaseFile)
        cursor = await connection.execute(
            '''
                SELECT category, correctAnswer, difficulty, question, questionId, wrongAnswer1, wrongAnswer2, wrongAnswer3 FROM tdQuestions
                ORDER BY RANDOM()
                LIMIT 1
            '''
        )

        row = await cursor.fetchone()
        if not utils.hasItems(row) or len(row) != 8:
            raise RuntimeError(f'Received malformed data from TD database: {row}')

        triviaQuestionDict: Dict[str, Any] = {
            'category': row[0],
            'correctAnswer': row[1],
            'difficulty': row[2],
            'question': row[3],
            'triviaId': row[4],
            'wrongAnswers': [ row[5], row[6], row[7] ]
        }

        await cursor.close()
        await connection.close()
        return triviaQuestionDict

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.TRIVIA_DATABASE
