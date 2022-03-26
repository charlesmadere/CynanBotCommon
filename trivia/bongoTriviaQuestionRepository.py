import random
from datetime import datetime, timedelta, timezone
from json.decoder import JSONDecodeError
from typing import Dict, List, Tuple

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
    from CynanBotCommon.trivia.jokeTriviaRepository import JokeTriviaRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.triviaVerifier import TriviaVerifier
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.jokeTriviaRepository import JokeTriviaRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.triviaVerifier import TriviaVerifier
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class BongoTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaIdGenerator is None:
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__timber: Timber = timber
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator

    def fetchTriviaQuestion(self) -> AbsTriviaQuestion:
        self.__timber.log('BongoTriviaRepository', 'Fetching trivia question...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://beta-trivia.bongo.best/?limit=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('BongoTriviaRepository', f'Exception occurred when attempting to fetch trivia from Bongo: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('BongoTriviaRepository', f'Encountered non-200 HTTP status code from Bongo: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: List[Dict[str, object]] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('BongoTriviaRepository', f'Exception occurred when attempting to decode Bongo\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Bongo\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('BongoTriviaRepository', f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')

        triviaJson: Dict[str, object] = jsonResponse[0]

        if not utils.hasItems(triviaJson):
            self.__timber.log('BongoTriviaRepository', f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(utils.getStrFromDict(triviaJson, 'difficulty', fallback = ''))
        triviaType = TriviaType.fromStr(utils.getStrFromDict(triviaJson, 'type'))
        category = utils.getStrFromDict(triviaJson, 'category', fallback = '', clean = True, htmlUnescape = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True, htmlUnescape = True)

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = self.__triviaIdGenerator.generate(
                category = category,
                difficulty = triviaDifficulty.toStr(),
                question = question
            )

        if triviaType is TriviaType.MULTIPLE_CHOICE:



