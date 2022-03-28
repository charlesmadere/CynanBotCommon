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


class OpenTriviaDatabaseTriviaQuestionRepository(AbsTriviaQuestionRepository):

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
        self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', 'Fetching trivia question...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://opentdb.com/api.php?amount=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Exception occurred when attempting to fetch trivia question: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Encountered non-200 HTTP status code: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s data due to null/empty JSON contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s data due to null/empty JSON contents: {jsonResponse}')
        elif utils.getIntFromDict(jsonResponse, 'response_code', fallback = -1) != 0:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s data due to bad \"response_code\" value: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s data due to bad \"response_code\" value: {jsonResponse}')
        elif not utils.hasItems(jsonResponse.get('results')):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s data due to missing/null/empty \"results\" array: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s data due to missing/null/empty \"results\" array: {jsonResponse}')

        resultJson: Dict[str, object] = jsonResponse['results'][0]
        if not utils.hasItems(resultJson):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s data due to null/empty \"results\" contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(utils.getStrFromDict(resultJson, 'difficulty', fallback = ''))
        triviaType = TriviaType.fromStr(utils.getStrFromDict(resultJson, 'type'))
        category = utils.getStrFromDict(resultJson, 'category', fallback = '', clean = True, htmlUnescape = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True, htmlUnescape = True)

        triviaId = self._triviaIdGenerator.generate(
            category = category,
            difficulty = triviaDifficulty.toStr(),
            question = question
        )

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswer = utils.getStrFromDict(resultJson, 'correct_answer', clean = True, htmlUnescape = True)
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            multipleChoiceResponses = self._buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponsesJson = resultJson['incorrect_answers']
            )

            if self._verifyIsActuallyMultipleChoiceQuestion(correctAnswers, multipleChoiceResponses):
                return MultipleChoiceTriviaQuestion(
                    correctAnswers = correctAnswers,
                    multipleChoiceResponses = multipleChoiceResponses,
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = triviaDifficulty,
                    triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
                )
            else:
                triviaType = TriviaType.TRUE_FALSE

        if triviaType is TriviaType.TRUE_FALSE:
            correctAnswer = utils.getBoolFromDict(resultJson, 'correct_answer')
            correctAnswers: List[bool] = list()
            correctAnswers.append(correctAnswer)

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Open Trivia Database: {jsonResponse}')
