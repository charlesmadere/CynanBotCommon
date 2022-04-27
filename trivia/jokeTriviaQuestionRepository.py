import json
import random
from os import path
from typing import Dict, List, Optional

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
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import UnsupportedTriviaTypeException
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class JokeTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        jokeTriviaQuestionFile: str = 'CynanBotCommon/trivia/jokeTriviaQuestionRepository.json'
    ):
        super().__init__(triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidStr(jokeTriviaQuestionFile):
            raise ValueError(f'jokeTriviaQuestionFile argument is malformed: \"{jokeTriviaQuestionFile}\"')

        self.__timber: Timber = timber
        self.__jokeTriviaQuestionFile: str = jokeTriviaQuestionFile

    async def fetchTriviaQuestion(self, twitchChannel: Optional[str]) -> AbsTriviaQuestion:
        self.__timber.log('JokeTriviaQuestionRepository', 'Fetching trivia question...')

        triviaJson: Optional[Dict[str, object]] = await self.__fetchTriviaQuestionJson(twitchChannel)

        if not utils.hasItems(triviaJson):
            return None

        category = utils.getStrFromDict(triviaJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True)
        triviaDifficulty = TriviaDifficulty.fromStr(triviaJson.get('difficulty'))
        triviaId = utils.getStrFromDict(triviaJson, 'id')
        triviaType = TriviaType.fromStr(utils.getStrFromDict(triviaJson, 'type'))

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswers: List[str] = triviaJson['correctAnswers']
            multipleChoiceResponses: List[str] = triviaJson['responses']
            random.shuffle(multipleChoiceResponses)

            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                triviaId = triviaId,
                question = question,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.JOKE_TRIVIA_REPOSITORY
            )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswers: List[bool] = triviaJson['correctAnswers']

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                triviaId = triviaId,
                question = question,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.JOKE_TRIVIA_REPOSITORY
            )
        else:
            raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Joke Trivia Question Repository: {triviaJson}')

    async def __fetchTriviaQuestionJson(self, twitchChannel: Optional[str]) -> Optional[Dict[str, object]]:
        jsonContents = await self.__readAllJson()

        triviaQuestions: List[Dict[str, object]] = jsonContents.get('triviaQuestions')
        if not utils.hasItems(triviaQuestions):
            return None

        acceptableTriviaQuestions: List[Dict[str, object]] = list()

        for triviaQuestion in triviaQuestions:
            compatibleWith: Optional[List[str]] = triviaQuestion.get('compatibleWith')

            if utils.hasItems(compatibleWith):
                if utils.isValidStr(twitchChannel):
                    for tc in compatibleWith:
                        if tc.lower() == twitchChannel.lower():
                            acceptableTriviaQuestions.append(triviaQuestion)
                            break
            else:
                acceptableTriviaQuestions.append(triviaQuestion)

        if utils.hasItems(acceptableTriviaQuestions):
            return random.choice(acceptableTriviaQuestions)
        else:
            return None

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE, TriviaType.TRUE_FALSE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.JOKE_TRIVIA_REPOSITORY

    async def __readAllJson(self) -> Dict[str, object]:
        if not path.exists(self.__jokeTriviaQuestionFile):
            raise FileNotFoundError(f'Joke trivia question file not found: \"{self.__jokeTriviaQuestionFile}\"')

        with open(self.__jokeTriviaQuestionFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from joke trivia file: \"{self.__jokeTriviaQuestionFile}\"')

        return jsonContents
