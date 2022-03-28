import random
from datetime import datetime, timedelta, timezone
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
    from CynanBotCommon.trivia.bongoTriviaQuestionRepository import \
        BongoTriviaQuestionRepository
    from CynanBotCommon.trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from CynanBotCommon.trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import \
        TooManyTriviaFetchAttemptsException
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaVerifier import TriviaVerifier
    from CynanBotCommon.trivia.willFryTriviaQuestionRepository import \
        WillFryTriviaQuestionRepository
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import TooManyTriviaFetchAttemptsException
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaVerifier import TriviaVerifier


class TriviaRepository():

    def __init__(
        self,
        bongoTriviaQuestionRepository: BongoTriviaQuestionRepository,
        jokeTriviaQuestionRepository: JokeTriviaQuestionRepository,
        openTriviaDatabaseTriviaQuestionRepository: OpenTriviaDatabaseTriviaQuestionRepository,
        quizApiTriviaQuestionRepository: QuizApiTriviaQuestionRepository,
        timber: Timber,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaVerifier: TriviaVerifier,
        willFryTriviaQuestionRepository: WillFryTriviaQuestionRepository,
        cacheTimeDelta: timedelta = timedelta(minutes = 2, seconds = 30)
    ):
        if bongoTriviaQuestionRepository is None:
            raise ValueError(f'bongoTriviaQuestionRepository argument is malformed: \"{bongoTriviaQuestionRepository}\"')
        elif jokeTriviaQuestionRepository is None:
            raise ValueError(f'jokeTriviaQuestionRepository argument is malformed: \"{jokeTriviaQuestionRepository}\"')
        elif openTriviaDatabaseTriviaQuestionRepository is None:
            raise ValueError(f'openTriviaDatabaseTriviaQuestionRepository argument is malformed: \"{openTriviaDatabaseTriviaQuestionRepository}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaIdGenerator is None:
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif triviaVerifier is None:
            raise ValueError(f'triviaVerifier argument is malformed: \"{triviaVerifier}\"')
        elif willFryTriviaQuestionRepository is None:
            raise ValueError(f'willFryTriviaQuestionRepository argument is malformed: \"{willFryTriviaQuestionRepository}\"')

        self.__bongoTriviaQuestionRepository: AbsTriviaQuestionRepository = bongoTriviaQuestionRepository
        self.__jokeTriviaQuestionRepository: AbsTriviaQuestionRepository = jokeTriviaQuestionRepository
        self.__openTriviaDatabaseTriviaQuestionRepository: AbsTriviaQuestionRepository = openTriviaDatabaseTriviaQuestionRepository
        self.__quizApiTriviaQuestionRepository: AbsTriviaQuestionRepository = quizApiTriviaQuestionRepository
        self.__timber: Timber = timber
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__triviaVerifier: TriviaVerifier = triviaVerifier
        self.__willFryTriviaQuestionRepository: AbsTriviaQuestionRepository = willFryTriviaQuestionRepository

        if cacheTimeDelta is None:
            self.__cacheTime = None
        else:    
            self.__cacheTime = datetime.now(timezone.utc) - cacheTimeDelta

        self.__cacheTimeDelta: timedelta = cacheTimeDelta
        self.__triviaResponse: AbsTriviaQuestion = None

    def __chooseRandomTriviaSource(
        self,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> TriviaSource:
        if not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        triviaSourcesAndWeights: Dict[TriviaSource, int] = self.__triviaSettingsRepository.getAvailableTriviaSourcesAndWeights()

        if not isJokeTriviaRepositoryEnabled and TriviaSource.JOKE_TRIVIA_REPOSITORY in triviaSourcesAndWeights:
            del triviaSourcesAndWeights[TriviaSource.JOKE_TRIVIA_REPOSITORY]

        if not self.__isQuizApiAvailable() and TriviaSource.QUIZ_API in triviaSourcesAndWeights:
            del triviaSourcesAndWeights[TriviaSource.QUIZ_API]

        if not utils.hasItems(triviaSourcesAndWeights):
            raise RuntimeError(f'There are no trivia sources available to be fetched from!')

        triviaSources: List[TriviaSource] = list()
        triviaWeights: List[int] = list()

        for triviaSource in triviaSourcesAndWeights:
            triviaSources.append(triviaSource)
            triviaWeights.append(triviaSourcesAndWeights[triviaSource])

        randomChoices = random.choices(triviaSources, triviaWeights)
        if not utils.hasItems(triviaSources):
            raise RuntimeError(f'Trivia sources returned by random.choices() is malformed: \"{randomChoices}\"')

        return randomChoices[0]

    def __fetchTriviaQuestionFromJService(self) -> AbsTriviaQuestion:
        self.__timber.log('TriviaRepository', 'Fetching trivia question from jService...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://jservice.io/api/random',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to fetch trivia from jService: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('TriviaRepository', f'Encountered non-200 HTTP status code from jService: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: List[Dict[str, object]] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to decode jService\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode jService\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TriviaRepository', f'Rejecting jService data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService data due to null/empty contents: {jsonResponse}')

        resultJson: Dict[str, object] = jsonResponse[0]

        if not utils.hasItems(resultJson):
            self.__timber.log('TriviaRepository', f'Rejecting jService data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService data due to null/empty contents: {jsonResponse}')

        category = utils.getStrFromDict(resultJson['category'], 'title', fallback = '', clean = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True)

        triviaId = utils.getStrFromDict(resultJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = self.__triviaIdGenerator.generate(category = category, question = question)

        correctAnswer = utils.getStrFromDict(resultJson, 'answer', clean = True)
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

    def fetchTrivia(
        self,
        twitchChannel: str,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        now = datetime.now(timezone.utc)

        if self.__cacheTimeDelta is None or self.__cacheTime is None or self.__cacheTime + self.__cacheTimeDelta < now or self.__triviaResponse is None:
            self.__triviaResponse = self.__fetchTrivia(
                twitchChannel = twitchChannel,
                isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
            )
            self.__cacheTime = now

        return self.__triviaResponse

    def __fetchTrivia(
        self,
        twitchChannel: str,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        triviaSource = self.__chooseRandomTriviaSource(
            isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
        )

        triviaQuestion: AbsTriviaQuestion = None
        retryCount = 0
        maxRetryCount = self.__triviaSettingsRepository.getMaxRetryCount()
        attemptedTriviaSources: List[TriviaSource] = list()

        while retryCount < maxRetryCount:
            attemptedTriviaSources.append(triviaSource)

            if triviaSource is TriviaSource.BONGO:
                triviaQuestion = self.__bongoTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.JOKE_TRIVIA_REPOSITORY:
                triviaQuestion = self.__jokeTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.J_SERVICE:
                triviaQuestion = self.__fetchTriviaQuestionFromJService()
            elif triviaSource is TriviaSource.OPEN_TRIVIA_DATABASE:
                triviaQuestion = self.__openTriviaDatabaseTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.QUIZ_API:
                triviaQuestion = self.__quizApiTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.WILL_FRY_TRIVIA_API:
                triviaQuestion = self.__willFryTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            else:
                raise ValueError(f'unknown TriviaSource: \"{triviaSource}\"')

            if self.__verifyGoodTriviaQuestion(triviaQuestion, twitchChannel):
                return triviaQuestion
            else:
                triviaSource = self.__chooseRandomTriviaSource(
                   isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
                )

                retryCount = retryCount + 1

        raise TooManyTriviaFetchAttemptsException(f'Unable to fetch trivia from {attemptedTriviaSources} after {retryCount} attempts (max attempts is {maxRetryCount})')

    def __isQuizApiAvailable(self) -> bool:
        return self.__quizApiTriviaQuestionRepository is not None

    def __verifyGoodTriviaQuestion(
        self,
        triviaQuestion: AbsTriviaQuestion,
        twitchChannel: str
    ) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        triviaContentCode = self.__triviaVerifier.verify(triviaQuestion, twitchChannel)

        if triviaContentCode == TriviaContentCode.OK:
            return True
        else:
            self.__timber.log('TriviaRepository', f'Rejected a trivia question due to content code: {triviaContentCode}')
            return False
