from typing import Any, Dict, List, Optional, Set

import aiofiles
import aiofiles.ospath
import aiosqlite

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
    from CynanBotCommon.trivia.triviaRepositories.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timberInterface import TimberInterface
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaRepositories.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class WwtbamTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: TimberInterface,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepositoryInterface,
        triviaDatabaseFile: str = 'CynanBotCommon/trivia/questionSources/wwtbamTriviaQuestionDatabase.sqlite'
    ):
        super().__init__(triviaSettingsRepository)

        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaQuestionCompiler, TriviaQuestionCompiler):
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')
        elif not utils.isValidStr(triviaDatabaseFile):
            raise ValueError(f'triviaDatabaseFile argument is malformed: \"{triviaDatabaseFile}\"')

        self.__timber: TimberInterface = timber
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler
        self.__triviaDatabaseFile: str = triviaDatabaseFile

        self.__hasQuestionSetAvailable: Optional[bool] = None

    async def fetchTriviaQuestion(self, fetchOptions: TriviaFetchOptions) -> AbsTriviaQuestion:
        if not isinstance(fetchOptions, TriviaFetchOptions):
            raise ValueError(f'fetchOptions argument is malformed: \"{fetchOptions}\"')

        self.__timber.log('WwtbamTriviaQuestionRepository', f'Fetching trivia question... (fetchOptions={fetchOptions})')

        triviaDict = await self.__fetchTriviaQuestionDict()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('WwtbamTriviaQuestionRepository', f'{triviaDict}')

        triviaId = utils.getStrFromDict(triviaDict, 'triviaId')

        question = utils.getStrFromDict(triviaDict, 'question')
        question = await self.__triviaQuestionCompiler.compileQuestion(question)

        responses: List[str] = list()
        responses.append(utils.getStrFromDict(triviaDict, 'responseA'))
        responses.append(utils.getStrFromDict(triviaDict, 'responseB'))
        responses.append(utils.getStrFromDict(triviaDict, 'responseC'))
        responses.append(utils.getStrFromDict(triviaDict, 'responseD'))

        correctAnswerIndex = utils.getStrFromDict(triviaDict, 'correctAnswer', clean = True)

        correctAnswer: Optional[str] = None
        if correctAnswerIndex.lower() == 'a':
            correctAnswer = responses[0]
        elif correctAnswerIndex.lower() == 'b':
            correctAnswer = responses[1]
        elif correctAnswerIndex.lower() == 'c':
            correctAnswer = responses[2]
        elif correctAnswerIndex.lower() == 'd':
            correctAnswer = responses[3]

        if not utils.isValidStr(correctAnswer):
            raise RuntimeError(f'Unknown correctAnswerIndex: \"{correctAnswerIndex}\"')

        correctAnswers: List[str] = list()
        correctAnswers.append(correctAnswer)

        correctAnswers = await self.__triviaQuestionCompiler.compileResponses(correctAnswers)
        responses = await self.__triviaQuestionCompiler.compileResponses(responses)

        multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = responses
        )

        return MultipleChoiceTriviaQuestion(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = multipleChoiceResponses,
            category = None,
            categoryId = None,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.WWTBAM
        )

    async def __fetchTriviaQuestionDict(self) -> Dict[str, Any]:
        if not await aiofiles.ospath.exists(self.__triviaDatabaseFile):
            raise FileNotFoundError(f'WWTBAM trivia database file not found: \"{self.__triviaDatabaseFile}\"')

        connection = await aiosqlite.connect(self.__triviaDatabaseFile)
        cursor = await connection.execute(
            '''
                SELECT correctAnswer, question, responseA, responseB, responseC, responseD, triviaId FROM wwtbamTriviaQuestions
                ORDER BY RANDOM()
                LIMIT 1
            '''
        )

        row = await cursor.fetchone()
        if not utils.hasItems(row) or len(row) != 7:
            raise RuntimeError(f'Received malformed data from WWTBAM database: {row}')

        triviaQuestionDict: Dict[str, Any] = {
            'correctAnswer': row[0],
            'question': row[1],
            'responseA': row[2],
            'responseB': row[3],
            'responseC': row[4],
            'responseD': row[5],
            'triviaId': row[6]
        }

        await cursor.close()
        await connection.close()
        return triviaQuestionDict

    def getSupportedTriviaTypes(self) -> Set[TriviaType]:
        return { TriviaType.MULTIPLE_CHOICE }

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.WWTBAM

    async def hasQuestionSetAvailable(self) -> bool:
        if self.__hasQuestionSetAvailable is not None:
            return self.__hasQuestionSetAvailable

        hasQuestionSetAvailable = await aiofiles.ospath.exists(self.__triviaDatabaseFile)
        self.__hasQuestionSetAvailable = hasQuestionSetAvailable

        return hasQuestionSetAvailable
