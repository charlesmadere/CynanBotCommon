import json
import random
from os import path
from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
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
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class JokeTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository,
        jokeTriviaFile: str = 'CynanBotCommon/trivia/jokeTriviaRepository.json'
    ):
        super().__init__(triviaIdGenerator, triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidStr(jokeTriviaFile):
            raise ValueError(f'jokeTriviaFile argument is malformed: \"{jokeTriviaFile}\"')

        self.__timber: Timber = timber
        self.__jokeTriviaFile: str = jokeTriviaFile

    def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        questionJson: Dict[str, object] = None
        retryCount = 0
        maxRetryCount = self.__getMaxRetryCount()

        while questionJson is None and retryCount <= maxRetryCount:
            questionJson = self.__fetchTriviaQuestionJson()

            compatibleWith: List[str] = questionJson.get('compatibleWith')
            if not self.__isCompatible(compatibleWith, twitchChannel):
                questionJson = None

            retryCount = retryCount + 1

        if not utils.hasItems(questionJson):
            self.__timber.log('JokeTriviaRepository', f'Failed to find a compatible trivia question after {retryCount} retries')
            return None

        category = utils.getStrFromDict(questionJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(questionJson, 'question', clean = True)
        triviaDifficulty = TriviaDifficulty.fromStr(questionJson.get('difficulty'))
        triviaId = utils.getStrFromDict(questionJson, 'id')
        triviaType = TriviaType.fromStr(utils.getStrFromDict(questionJson, 'type'))

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswers: List[str] = questionJson['correctAnswers']
            multipleChoiceResponses: List[str] = questionJson['responses']
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
        elif triviaType is TriviaType.QUESTION_ANSWER:
            correctAnswers: List[str] = questionJson['correctAnswers']

            return QuestionAnswerTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                triviaId = triviaId,
                question = question,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.JOKE_TRIVIA_REPOSITORY
            )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswers: List[bool] = questionJson['correctAnswers']

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                triviaId = triviaId,
                question = question,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.JOKE_TRIVIA_REPOSITORY
            )
        else:
            raise ValueError(f'triviaType \"{triviaType}\" is unknown for Local Trivia Repository: {questionJson}')

    def __fetchTriviaQuestionJson(self) -> Dict[str, object]:
        jsonContents = self.__readAllJson()

        triviaQuestions: List[Dict[str, object]] = jsonContents.get('triviaQuestions')
        if not utils.hasItems(triviaQuestions):
            raise ValueError(f'\"triviaQuestions\" field in joke trivia file \"{self.__jokeTriviaFile}\" is malformed: \"{triviaQuestions}\"')

        return random.choice(triviaQuestions)

    def __getMaxRetryCount(self) -> int:
        jsonContents = self.__readAllJson()
        return utils.getIntFromDict(jsonContents, 'maxRetryCount', 5)

    def __isCompatible(self, compatibleWith: List[str], twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if not utils.hasItems(compatibleWith):
            return True

        for tc in compatibleWith:
            if tc.lower() == twitchChannel.lower():
                return True

        return False

    def __readAllJson(self) -> Dict[str, object]:
        if not path.exists(self.__jokeTriviaFile):
            raise FileNotFoundError(f'Joke trivia file not found: \"{self.__jokeTriviaFile}\"')

        with open(self.__jokeTriviaFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from joke trivia file: \"{self.__jokeTriviaFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of joke trivia file \"{self.__jokeTriviaFile}\" is empty')

        return jsonContents
