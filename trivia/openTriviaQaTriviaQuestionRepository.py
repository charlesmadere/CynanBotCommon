from typing import Dict, List, Optional

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
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import UnsupportedTriviaTypeException
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class OpenTriviaQaTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaDatabaseFile: str = 'CynanBotCommon/trivia/openTriviaQaTriviaQuestionDatabase.sqlite'
    ):
        super().__init__(triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidStr(triviaDatabaseFile):
            raise ValueError(f'triviaDatabaseFile argument is malformed: \"{triviaDatabaseFile}\"')

        self.__timber: Timber = timber
        self.__triviaDatabaseFile: str = triviaDatabaseFile

    async def fetchTriviaQuestion(self, twitchChannel: Optional[str]) -> AbsTriviaQuestion:
        self.__timber.log('OpenTriviaQaTriviaQuestionRepository', 'Fetching trivia question...')

        triviaDict = await self.__fetchTriviaQuestionDict()

        category = utils.getStrFromDict(triviaDict, 'category', clean = True)
        question = utils.getStrFromDict(triviaDict, 'question', clean = True)
        triviaId = utils.getStrFromDict(triviaDict, 'questionId')
        triviaType = TriviaType.fromStr(utils.getStrFromDict(triviaDict, 'questionType'))

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswer = utils.getStrFromDict(triviaDict, 'correctAnswer', clean = True)
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            responses: List[str] = list()
            responses.append(utils.getStrFromDict(triviaDict, 'response1', clean = True))
            responses.append(utils.getStrFromDict(triviaDict, 'response2', clean = True))
            responses.append(utils.getStrFromDict(triviaDict, 'response3', clean = True))
            responses.append(utils.getStrFromDict(triviaDict, 'response4', clean = True))

            multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = responses
            )

            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = TriviaDifficulty.UNKNOWN,
                triviaSource = TriviaSource.OPEN_TRIVIA_QA
            )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswer = utils.getBoolFromDict(triviaDict, 'correctAnswer')
            correctAnswers: List[bool] = list()
            correctAnswers.append(correctAnswer)

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = TriviaDifficulty.UNKNOWN,
                triviaSource = TriviaSource.OPEN_TRIVIA_QA
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for OpenTriviaQaTriviaQuestion: {triviaDict}')

    async def __fetchTriviaQuestionDict(self) -> Dict[str, object]:
        connection = await aiosqlite.connect(self.__triviaDatabaseFile)
        cursor = await connection.execute(
            '''
                SELECT correctAnswer, newCategory, question, questionId, questionType, response1, response2, response3, response4 FROM triviaQuestions
                ORDER BY RANDOM()
                LIMIT 1
            '''
        )

        row = await cursor.fetchone()
        if not utils.hasItems(row) or len(row) != 9:
            raise RuntimeError(f'Received malformed data from OpenTriviaQaTriviaQuestion database: {row}')

        triviaQuestionDict: Dict[str, object] = {
            'category': row[1],
            'correctAnswer': row[0],
            'question': row[2],
            'questionId': row[3],
            'questionType': row[4],
            'response1': row[5],
            'response2': row[6],
            'response3': row[7],
            'response4': row[8]
        }

        await cursor.close()
        await connection.close()
        return triviaQuestionDict

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE, TriviaType.TRUE_FALSE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.OPEN_TRIVIA_QA
