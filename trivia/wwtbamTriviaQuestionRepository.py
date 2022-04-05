from typing import Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backingDatabase import BackingDatabase
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
    from backingDatabase import BackingDatabase
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource


class WwtbamTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaDatabaseFile: str = 'CynanBotCommon/trivia/wwtbamDatabase.sqlite'
    ):
        super().__init__(triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidStr(triviaDatabaseFile):
            raise ValueError(f'triviaDatabaseFile argument is malformed: \"{triviaDatabaseFile}\"')

        self.__timber: Timber = timber
        self.__backingDatabase: BackingDatabase = BackingDatabase(triviaDatabaseFile)

    async def fetchTriviaQuestion(self, twitchChannel: Optional[str]) -> AbsTriviaQuestion:
        self.__timber.log('WwtbamTriviaQuestionRepository', 'Fetching trivia question...')

        triviaDict = await self.__fetchTriviaQuestionDict()

        triviaId = utils.getStrFromDict(triviaDict, 'triviaId')
        question = utils.getStrFromDict(triviaDict, 'question', clean = True)

        correctAnswer = utils.getStrFromDict(triviaDict, 'correctAnswer', clean = True)
        correctAnswers: List[str] = list()
        correctAnswers.append(correctAnswer)

        responses: List[str] = list()
        responses.append(utils.getStrFromDict(triviaDict, 'responseA', clean = True))
        responses.append(utils.getStrFromDict(triviaDict, 'responseB', clean = True))
        responses.append(utils.getStrFromDict(triviaDict, 'responseC', clean = True))
        responses.append(utils.getStrFromDict(triviaDict, 'responseD', clean = True))

        multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
            correctAnswers = correctAnswers,
            multipleChoiceResponsesJson = responses
        )

        return MultipleChoiceTriviaQuestion(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = multipleChoiceResponses,
            category = None,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.WWTBAM
        )

    async def __fetchTriviaQuestionDict(self) -> Dict[str, object]:
        cursor = self.__backingDatabase.getConnection().cursor()
        cursor.execute(
            '''
                SELECT correctAnswer, question, responseA, responseB, responseC, responseD, triviaId FROM wwtbamTriviaQuestions
                ORDER BY RANDOM()
                LIMIT 1
            '''
        )

        row = cursor.fetchone()

        return {
            'correctAnswer': row[0],
            'question': row[1],
            'responseA': row[2],
            'responseB': row[3],
            'responseC': row[4],
            'responseD': row[5],
            'triviaId': row[6]
        }
