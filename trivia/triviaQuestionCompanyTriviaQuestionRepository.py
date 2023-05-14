from typing import Any, Dict, List, Set

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
    from CynanBotCommon.trivia.triviaExceptions import \
        UnsupportedTriviaTypeException
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
    from trivia.triviaExceptions import UnsupportedTriviaTypeException
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class TriviaQuestionCompanyTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaDatabaseFile: str = 'CynanBotCommon/trivia/questionSources/triviaQuestionCompanyTriviaQuestionRepository.sqlite'
    ):
        super().__init__(triviaSettingsRepository)

        if not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaQuestionCompiler, TriviaQuestionCompiler):
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')
        elif not utils.isValidStr(triviaDatabaseFile):
            raise ValueError(f'triviaDatabaseFile argument is malformed: \"{triviaDatabaseFile}\"')

        self.__timber: Timber = timber
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler
        self.__triviaDatabaseFile: str = triviaDatabaseFile

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('TriviaQuestionCompanyTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        triviaDict = await self.__fetchTriviaQuestionDict()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('TriviaQuestionCompanyTriviaQuestionRepository', f'{triviaDict}')

        difficulty = TriviaDifficulty.fromInt(utils.getIntFromDict(triviaDict, 'difficulty'))
        questionId = utils.getStrFromDict(triviaDict, 'questionId')
        questionType = TriviaType.fromStr(utils.getStrFromDict(triviaDict, 'questionType'))

        category = await self.__triviaQuestionCompiler.compileCategory(utils.getStrFromDict(triviaDict, 'category'))
        question = await self.__triviaQuestionCompiler.compileQuestion(utils.getStrFromDict(triviaDict, 'question'))

        if questionType is TriviaType.MULTIPLE_CHOICE:
            responses: List[str] = triviaDict['responses']
            correctAnswer: str = responses[utils.getIntFromDict(triviaDict, 'correctAnswerIndex')]
            correctAnswer = await self.__triviaQuestionCompiler.compileResponse(correctAnswer)
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            responses = await self.__triviaQuestionCompiler.compileResponses(responses)

            multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = responses
            )

            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                categoryId = None,
                question = question,
                triviaId = questionId,
                triviaDifficulty = difficulty,
                triviaSource = self.getTriviaSource()
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{questionType}\" is not supported for {self.getTriviaSource()}: {triviaDict}')

    async def __fetchTriviaQuestionDict(self) -> Dict[str, Any]:
        connection = await aiosqlite.connect(self.__triviaDatabaseFile)
        cursor = await connection.execute(
            '''
                SELECT category, correctAnswerIndex, difficulty, question, questionId, questionType, response0, response1, response2, response3 FROM tqcQuestions
                ORDER BY RANDOM()
                LIMIT 1
            '''
        )

        row = await cursor.fetchone()
        if not utils.hasItems(row) or len(row) != 10:
            raise RuntimeError(f'Received malformed data from {self.getTriviaSource()} database: {row}')

        questionDict: Dict[str, Any] = {
            'category': row[0],
            'correctAnswerIndex': row[1],
            'difficulty': row[2],
            'question': row[3],
            'questionId': row[4],
            'questionType': row[5],
            'responses': [ row[6], row[7], row[8], row[9] ]
        }

        await cursor.close()
        await connection.close()
        return questionDict

    def getSupportedTriviaTypes(self) -> Set[TriviaType]:
        return { TriviaType.MULTIPLE_CHOICE }

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.THE_QUESTION_CO
