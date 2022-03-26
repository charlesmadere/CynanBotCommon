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


class TriviaRepository():

    def __init__(
        self,
        jokeTriviaRepository: JokeTriviaRepository,
        timber: Timber,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaVerifier: TriviaVerifier,
        quizApiKey: str = None,
        cacheTimeDelta: timedelta = timedelta(minutes = 2, seconds = 30)
    ):
        if jokeTriviaRepository is None:
            raise ValueError(f'jokeTriviaRepository argument is malformed: \"{jokeTriviaRepository}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaIdGenerator is None:
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif triviaVerifier is None:
            raise ValueError(f'triviaVerifier argument is malformed: \"{triviaVerifier}\"')

        self.__jokeTriviaRepository: JokeTriviaRepository = jokeTriviaRepository
        self.__timber: Timber = timber
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__triviaVerifier: TriviaVerifier = triviaVerifier
        self.__quizApiKey: str = quizApiKey

        if cacheTimeDelta is None:
            self.__cacheTime = None
        else:    
            self.__cacheTime = datetime.now(timezone.utc) - cacheTimeDelta

        self.__cacheTimeDelta: timedelta = cacheTimeDelta
        self.__triviaResponse: AbsTriviaQuestion = None

    def __buildMultipleChoiceResponsesList(
        self,
        correctAnswers: List[str],
        multipleChoiceResponsesJson: List[str]
    ) -> List[str]:
        if not utils.hasItems(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')
        elif not utils.hasItems(multipleChoiceResponsesJson):
            raise ValueError(f'multipleChoiceResponsesJson argument is malformed: \"{multipleChoiceResponsesJson}\"')

        maxMultipleChoiceResponses = self.__triviaSettingsRepository.getMaxMultipleChoiceResponses()
        multipleChoiceResponses: List[str] = list()

        for correctAnswer in correctAnswers:
            multipleChoiceResponses.append(correctAnswer)

        # Annoyingly, I've encountered a few situations where we can have a question with more
        # than one of the same multiple choice answers. The below logic takes some steps to make
        # sure this doesn't happen, while also ensuring that we don't have too many multiple
        # choice responses.

        for incorrectAnswer in multipleChoiceResponsesJson:
            incorrectAnswer = utils.cleanStr(incorrectAnswer, htmlUnescape = True)
            add = True

            for response in multipleChoiceResponses:
                if incorrectAnswer.lower() == response.lower():
                    add = False
                    break

            if add:
                multipleChoiceResponses.append(incorrectAnswer)

                if len(multipleChoiceResponses) >= maxMultipleChoiceResponses:
                    break

        if not utils.hasItems(multipleChoiceResponses):
            raise ValueError(f'This trivia question doesn\'t have any multiple choice responses: \"{multipleChoiceResponses}\"')

        minMultipleChoiceResponses = self.__triviaSettingsRepository.getMinMultipleChoiceResponses()
        if len(multipleChoiceResponses) < minMultipleChoiceResponses:
            raise ValueError(f'This trivia question doesn\'t have enough multiple choice responses (minimum is {minMultipleChoiceResponses}): \"{multipleChoiceResponses}\"')

        multipleChoiceResponses.sort(key = lambda response: response.lower())
        return multipleChoiceResponses

    def __chooseRandomTriviaSource(
        self,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> TriviaSource:
        if not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        triviaSourcesAndWeights: Dict[TriviaSource, int] = self.__triviaSettingsRepository.getAvailableTriviaSourcesAndWeights()

        if not isJokeTriviaRepositoryEnabled and TriviaSource.JOKE_TRIVIA_REPOSITORY in triviaSourcesAndWeights:
            del triviaSourcesAndWeights[TriviaSource.JOKE_TRIVIA_REPOSITORY]

        if not self.__hasQuizApiKey() and TriviaSource.QUIZ_API in triviaSourcesAndWeights:
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

    def __fetchTriviaQuestionFromBongo(self) -> AbsTriviaQuestion:
        self.__timber.log('TriviaRepository', 'Fetching trivia question from Bongo...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://beta-trivia.bongo.best/?limit=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to fetch trivia from Bongo: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('TriviaRepository', f'Encountered non-200 HTTP status code from Bongo: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: List[Dict[str, object]] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to decode Bongo\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Bongo\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TriviaRepository', f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')

        triviaJson: Dict[str, object] = jsonResponse[0]

        if not utils.hasItems(triviaJson):
            self.__timber.log('TriviaRepository', f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')
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
            correctAnswer = utils.getStrFromDict(
                d = triviaJson,
                key = 'correct_answer',
                clean = True,
                htmlUnescape = True
            )
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            multipleChoiceResponses = self.__buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponsesJson = triviaJson['incorrect_answers']
            )

            if self.__isActuallyTrueFalseQuestion(correctAnswers, multipleChoiceResponses):
                return TrueFalseTriviaQuestion(
                    correctAnswers = utils.strsToBools(correctAnswers),
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = triviaDifficulty,
                    triviaSource = TriviaSource.BONGO
                )
            else:
                return MultipleChoiceTriviaQuestion(
                    correctAnswers = correctAnswers,
                    multipleChoiceResponses = multipleChoiceResponses,
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = triviaDifficulty,
                    triviaSource = TriviaSource.BONGO
                )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswer = utils.getBoolFromDict(triviaJson, 'correct_answer')
            correctAnswers: List[bool] = list()
            correctAnswers.append(correctAnswer)

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.BONGO
            )
        else:
            raise ValueError(f'triviaType \"{triviaType}\" is not supported for Bongo: {jsonResponse}')

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

    def __fetchTriviaQuestionFromJokeTriviaRepository(self, twitchChannel: str) -> AbsTriviaQuestion:
        self.__timber.log('TriviaRepository', 'Fetching trivia question from JokeTriviaRepository...')
        return self.__jokeTriviaRepository.fetchRandomQuestion(twitchChannel)

    def __fetchTriviaQuestionFromOpenTriviaDatabase(self) -> AbsTriviaQuestion:
        self.__timber.log('TriviaRepository', 'Fetching trivia question from Open Trivia Database...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://opentdb.com/api.php?amount=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to fetch trivia from Open Trivia Database: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('TriviaRepository', f'Encountered non-200 HTTP status code from Open Trivia Database: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TriviaRepository', f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')
        elif utils.getIntFromDict(jsonResponse, 'response_code', -1) != 0:
            self.__timber.log('TriviaRepository', f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
        elif not utils.hasItems(jsonResponse.get('results')):
            self.__timber.log('TriviaRepository', f'Rejecting trivia due to missing/null/empty \"results\" array: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to missing/null/empty \"results\" array: {jsonResponse}')

        resultJson: Dict[str, object] = jsonResponse['results'][0]

        if not utils.hasItems(resultJson):
            self.__timber.log('TriviaRepository', f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(utils.getStrFromDict(resultJson, 'difficulty', fallback = ''))
        triviaType = TriviaType.fromStr(utils.getStrFromDict(resultJson, 'type'))
        category = utils.getStrFromDict(resultJson, 'category', fallback = '', clean = True, htmlUnescape = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True, htmlUnescape = True)

        triviaId = self.__triviaIdGenerator.generate(
            category = category,
            difficulty = triviaDifficulty.toStr(),
            question = question
        )

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswer = utils.getStrFromDict(
                d = resultJson,
                key = 'correct_answer',
                clean = True,
                htmlUnescape = True
            )
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            multipleChoiceResponses = self.__buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponsesJson = resultJson['incorrect_answers']
            )

            if self.__isActuallyTrueFalseQuestion(correctAnswers, multipleChoiceResponses):
                return TrueFalseTriviaQuestion(
                    correctAnswers = utils.strsToBools(correctAnswers),
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = triviaDifficulty,
                    triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
                )
            else:
                return MultipleChoiceTriviaQuestion(
                    correctAnswers = correctAnswers,
                    multipleChoiceResponses = multipleChoiceResponses,
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = triviaDifficulty,
                    triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
                )
        elif triviaType is TriviaType.TRUE_FALSE:
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
        else:
            raise ValueError(f'triviaType \"{triviaType}\" is not supported for Open Trivia Database: {jsonResponse}')

    def __fetchTriviaQuestionFromQuizApi(self) -> AbsTriviaQuestion:
        self.__timber.log('TriviaRepository', 'Fetching trivia question from Quiz API...')

        if not self.__hasQuizApiKey():
            raise RuntimeError(f'Can\'t fetch trivia question from Quiz API as we have no key')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = f'https://quizapi.io/api/v1/questions?apiKey={self.__quizApiKey}&limit=1',
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0' # LOOOOL
                },
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to fetch trivia from Quiz API: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('TriviaRepository', f'Encountered non-200 HTTP status code from Quiz API: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to decode Quiz API\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Quiz API\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TriviaRepository', f'Rejecting Quiz API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Quiz API data due to null/empty contents: {jsonResponse}')

        triviaJson: Dict[str, object] = jsonResponse[0]
        if not utils.hasItems(triviaJson):
            self.__timber.log('TriviaRepository', f'Rejecting Quiz API\'s data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Quiz API\'s data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(utils.getStrFromDict(triviaJson, 'difficulty', fallback = ''))
        category = utils.getStrFromDict(triviaJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True)

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = self.__triviaIdGenerator.generate(
                category = category,
                difficulty = triviaDifficulty.toStr(),
                question = question
            )

        answersJson: Dict[str, str] = triviaJson['answers']
        answersList: List[Tuple[str, str]] = list(answersJson.items())
        answersList.sort(key = lambda entry: entry[0].lower())

        correctAnswersJson: Dict[str, str] = triviaJson['correct_answers']
        correctAnswersList: List[Tuple[str, str]] = list(correctAnswersJson.items())
        correctAnswersList.sort(key = lambda entry: entry[0].lower())

        if not utils.hasItems(answersList) or not utils.hasItems(correctAnswersList) or len(answersList) != len(correctAnswersList):
            raise ValueError(f'Rejecting Quiz API\'s data due to malformed \"answers\" and/or \"correct_answers\" data: {jsonResponse}')

        correctAnswers: List[str] = list()
        filteredAnswers: List[str] = list()

        for index, pair in enumerate(answersList):
            if utils.isValidStr(pair[0]) and utils.isValidStr(pair[1]):
                filteredAnswers.append(pair[1])
                correctAnswerPair: Tuple[str, str] = correctAnswersList[index]

                if utils.strToBool(correctAnswerPair[1]):
                    correctAnswers.append(pair[1])

        if not utils.hasItems(correctAnswers):
            raise ValueError(f'Rejecting Quiz API\'s data due to there being no correct answers: {jsonResponse}')

        multipleChoiceResponses = self.__buildMultipleChoiceResponsesList(
            correctAnswers = correctAnswers,
            multipleChoiceResponsesJson = filteredAnswers
        )

        if self.__isActuallyTrueFalseQuestion(correctAnswers, multipleChoiceResponses):
            return TrueFalseTriviaQuestion(
                correctAnswers = utils.strsToBools(correctAnswers),
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.QUIZ_API
            )
        else:
            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.QUIZ_API
            )

    def __fetchTriviaQuestionFromWillFryTriviaApi(self) -> AbsTriviaQuestion:
        self.__timber.log('TriviaRepository', 'Fetching trivia question from Will Fry Trivia API...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://the-trivia-api.com/questions?limit=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to fetch trivia from Will Fry Trivia API: {e}')
            return None

        if rawResponse.status_code != 200:
            self.__timber.log('TriviaRepository', f'Encountered non-200 HTTP status code from Will Fry Trivia API: \"{rawResponse.status_code}\"')
            return None

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TriviaRepository', f'Exception occurred when attempting to decode Will Fry Trivia API\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Will Fry Trivia API\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TriviaRepository', f'Rejecting Will Fry Trivia API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Will Fry Trivia API data due to null/empty contents: {jsonResponse}')

        resultJson: Dict[str, object] = jsonResponse[0]

        if not utils.hasItems(resultJson):
            self.__timber.log('TriviaRepository', f'Rejecting Will Fry Trivia API\'s data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Will Fry Trivia API\'s data due to null/empty contents: {jsonResponse}')

        triviaType = TriviaType.fromStr(utils.getStrFromDict(resultJson, 'type'))
        category = utils.getStrFromDict(resultJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True)

        triviaId = utils.getStrFromDict(resultJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = self.__triviaIdGenerator.generate(category = category, question = question)

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswer = utils.getStrFromDict(
                d = resultJson,
                key = 'correctAnswer',
                clean = True,
                htmlUnescape = True
            )
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            multipleChoiceResponses = self.__buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponsesJson = resultJson['incorrectAnswers']
            )

            if self.__isActuallyTrueFalseQuestion(correctAnswers, multipleChoiceResponses):
                return TrueFalseTriviaQuestion(
                    correctAnswers = utils.strsToBools(correctAnswers),
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = TriviaDifficulty.UNKNOWN,
                    triviaSource = TriviaSource.WILL_FRY_TRIVIA_API
                )
            else:
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
            raise ValueError(f'triviaType \"{triviaType}\" is not supported for Will Fry Trivia API: {jsonResponse}')

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
                triviaQuestion = self.__fetchTriviaQuestionFromBongo()
            elif triviaSource is TriviaSource.JOKE_TRIVIA_REPOSITORY:
                triviaQuestion = self.__fetchTriviaQuestionFromJokeTriviaRepository(twitchChannel)
            elif triviaSource is TriviaSource.J_SERVICE:
                triviaQuestion = self.__fetchTriviaQuestionFromJService()
            elif triviaSource is TriviaSource.OPEN_TRIVIA_DATABASE:
                triviaQuestion = self.__fetchTriviaQuestionFromOpenTriviaDatabase()
            elif triviaSource is TriviaSource.QUIZ_API:
                triviaQuestion = self.__fetchTriviaQuestionFromQuizApi()
            elif triviaSource is TriviaSource.WILL_FRY_TRIVIA_API:
                triviaQuestion = self.__fetchTriviaQuestionFromWillFryTriviaApi()
            else:
                raise ValueError(f'unknown TriviaSource: \"{triviaSource}\"')

            if self.__verifyGoodTriviaQuestion(triviaQuestion, twitchChannel):
                return triviaQuestion
            else:
                triviaSource = self.__chooseRandomTriviaSource(
                   isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
                )

                retryCount = retryCount + 1

        raise RuntimeError(f'Unable to fetch trivia from {attemptedTriviaSources} after {retryCount} attempts (max attempts is {maxRetryCount})')

    def __hasQuizApiKey(self) -> bool:
        return utils.isValidStr(self.__quizApiKey)

    def __isActuallyTrueFalseQuestion(
        self,
        correctAnswers: List[str],
        multipleChoiceResponses: List[str]
    ) -> bool:
        if not utils.hasItems(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')
        elif not utils.hasItems(multipleChoiceResponses):
            raise ValueError(f'multipleChoiceResponses argument is malformed: \"{multipleChoiceResponses}\"')

        for correctAnswer in correctAnswers:
            if correctAnswer.lower() != str(True).lower() and correctAnswer.lower() != str(False).lower():
                return False

        if len(multipleChoiceResponses) != 2:
            return False

        containsTrue = False
        containsFalse = False

        for response in multipleChoiceResponses:
            if response.lower() == str(True).lower():
                containsTrue = True
            elif response.lower() == str(False).lower():
                containsFalse = True

        return containsTrue and containsFalse

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
