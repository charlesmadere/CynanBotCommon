from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

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
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import UnsupportedTriviaTypeException
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class WillFryTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        super().__init__(triviaIdGenerator, triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: Timber = timber

    def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        self.__timber.log('WillFryTriviaQuestionRepository', 'Fetching trivia question...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://the-trivia-api.com/questions?limit=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('WillFryTriviaQuestionRepository', f'Exception occurred when attempting to fetch trivia: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('WillFryTriviaQuestionRepository', f'Encountered non-200 HTTP status code: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('WillFryTriviaQuestionRepository', f'Exception occurred when attempting to decode response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Will Fry Trivia response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('WillFryTriviaQuestionRepository', f'Rejecting JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Will Fry Trivia\'s JSON data due to null/empty contents: {jsonResponse}')

        triviaJson: Dict[str, object] = jsonResponse[0]
        if not utils.hasItems(triviaJson):
            self.__timber.log('WillFryTriviaQuestionRepository', f'Rejecting JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Will Fry Trivia\'s JSON data due to null/empty contents: {jsonResponse}')

        triviaType = TriviaType.fromStr(utils.getStrFromDict(triviaJson, 'type'))
        category = utils.getStrFromDict(triviaJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True)

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = self._triviaIdGenerator.generate(category = category, question = question)

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswer = utils.getStrFromDict(triviaJson, 'correctAnswer', clean = True, htmlUnescape = True)
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            multipleChoiceResponses = self._buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponsesJson = triviaJson['incorrectAnswers']
            )

            if self._verifyIsActuallyMultipleChoiceQuestion(correctAnswers, multipleChoiceResponses):
                return MultipleChoiceTriviaQuestion(
                    correctAnswers = correctAnswers,
                    multipleChoiceResponses = multipleChoiceResponses,
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = TriviaDifficulty.UNKNOWN,
                    triviaSource = TriviaSource.WILL_FRY_TRIVIA_API
                )
            else:
                self.__timber.log('WillFryTriviaQuestionRepository', f'Encountered a multiple choice question that is actually true/false')
                triviaType = TriviaType.TRUE_FALSE

        if triviaType is TriviaType.TRUE_FALSE:
            correctAnswer = utils.getBoolFromDict(triviaJson, 'correctAnswer')
            correctAnswers: List[bool] = list()
            correctAnswers.append(correctAnswer)

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = TriviaDifficulty.UNKNOWN,
                triviaSource = TriviaSource.WILL_FRY_TRIVIA_API
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Will Fry Trivia: {jsonResponse}')
