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
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import \
        UnsupportedTriviaTypeException
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import UnsupportedTriviaTypeException
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class JServiceTriviaQuestionRepository(AbsTriviaQuestionRepository):

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
        self.__timber.log('JServiceTriviaQuestionRepository', 'Fetching trivia question...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://jservice.io/api/random',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Exception occurred when attempting to fetch trivia: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Encountered non-200 HTTP status code: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: List[Dict[str, object]] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Exception occurred when attempting to decode jService\'s API response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode jService\'s API response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

        triviaJson: Dict[str, object] = jsonResponse[0]
        if not utils.hasItems(triviaJson):
            self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

        category = utils.getStrFromDict(triviaJson['category'], 'title', fallback = '', clean = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True)

        # this API seems to only ever give question and answer, so for now, we're just hardcoding this
        triviaType = TriviaType.QUESTION_ANSWER

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = self._triviaIdGenerator.generate(category = category, question = question)

        if triviaType is TriviaType.QUESTION_ANSWER:
            correctAnswer = utils.getStrFromDict(triviaJson, 'answer', clean = True)
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            return QuestionAnswerTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = TriviaDifficulty.UNKNOWN,
                triviaSource = TriviaSource.J_SERVICE
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for jService: {jsonResponse}')
