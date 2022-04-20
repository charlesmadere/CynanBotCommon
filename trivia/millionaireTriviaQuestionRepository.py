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
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource


class MillionaireTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaDatabaseFile: str = 'CynanBotCommon/trivia/millionaireTriviaQuestionsDatabase.sqlite'
    ):
        super().__init__(triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidStr(triviaDatabaseFile):
            raise ValueError(f'triviaDatabaseFile argument is malformed: \"{triviaDatabaseFile}\"')

        self.__timber: Timber = timber
        self.__triviaDatabaseFile: str = triviaDatabaseFile

    async def fetchTriviaQuestion(self, twitchChannel: Optional[str]) -> AbsTriviaQuestion:
        self.__timber.log('MillionaireTriviaQuestionRepository', 'Fetching trivia question...')

        triviaDict = await self.__fetchTriviaQuestionDict()

        triviaId = utils.getStrFromDict(triviaDict, 'triviaId')
        correctAnswer = utils.getStrFromDict(triviaDict, 'answer', clean = True)
        question = utils.getStrFromDict(triviaDict, 'question', clean = True)

        correctAnswers: List[str] = list()
        correctAnswers.append(correctAnswer)

        multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = triviaDict['responses']
        )

        return MultipleChoiceTriviaQuestion(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = multipleChoiceResponses,
            category = None,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.MILLIONAIRE
        )

    async def __fetchTriviaQuestionDict(self) -> Dict[str, object]:
        connection = await aiosqlite.connect(self.__triviaDatabaseFile)
        cursor = await connection.execute(
            '''
                SELECT answer, question, responseA, responseB, responseC, responseD, triviaId FROM millionaireQuestions
                ORDER BY RANDOM()
                LIMIT 1
            '''
        )

        row = await cursor.fetchone()
        if not utils.hasItems(row) or len(row) != 7:
            raise RuntimeError(f'Received malformed data from Millionaire database: {row}')

        triviaQuestionDict: Dict[str, object] = {
            'answer': row[0],
            'question': row[1],
            'responses': [ row[2], row[3], row[4], row[5] ],
            'triviaId': row[6]
        }

        await cursor.close()
        await connection.close()
        return triviaQuestionDict
