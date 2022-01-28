import json
import random
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from os import path
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.localTriviaRepository import \
        LocalTriviaRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.localTriviaRepository import LocalTriviaRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TriviaRepository():

    def __init__(
        self,
        localTriviaRepository: LocalTriviaRepository,
        triviaRepositoryFile: str = 'CynanBotCommon/trivia/triviaRepository.json',
        cacheTimeDelta: timedelta = timedelta(minutes = 2, seconds = 30)
    ):
        if localTriviaRepository is None:
            raise ValueError(f'localTriviaRepository argument is malformed: \"{localTriviaRepository}\"')
        elif not utils.isValidStr(triviaRepositoryFile):
            raise ValueError(f'triviaRepositoryFile argument is malformed: \"{triviaRepositoryFile}\"')

        self.__localTriviaRepository: LocalTriviaRepository = localTriviaRepository
        self.__triviaRepositoryFile: str = triviaRepositoryFile

        if cacheTimeDelta is None:
            self.__cacheTime = None
        else:    
            self.__cacheTime = datetime.utcnow() - cacheTimeDelta

        self.__cacheTimeDelta: timedelta = cacheTimeDelta
        self.__triviaResponse: AbsTriviaQuestion = None

    def __buildMultipleChoiceResponsesList(
        self,
        correctAnswer: str,
        multipleChoiceResponsesJson: List[str]
    ) -> List[str]:
        if not utils.isValidStr(correctAnswer):
            raise ValueError(f'correctAnswer argument is malformed: \"{correctAnswer}\"')
        elif not utils.hasItems(multipleChoiceResponsesJson):
            raise ValueError(f'multipleChoiceResponsesJson argument is malformed: \"{multipleChoiceResponsesJson}\"')

        maxMultipleChoiceResponses = self.__getMaxMultipleChoiceResponses()
        multipleChoiceResponses: List[str] = list()
        multipleChoiceResponses.append(correctAnswer)

        # Annoyingly, I've encountered a few situations where we can have a question with more
        # than one of the same multiple choice answers. The below logic takes some steps to make
        # sure this doesn't happen, while also ensuring that we don't have too many multiple
        # choice responses.

        for incorrectAnswer in multipleChoiceResponsesJson:
            incorrectAnswer = utils.cleanStr(incorrectAnswer, htmlUnescape = True)
            add: bool = True

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

        random.shuffle(multipleChoiceResponses)
        return multipleChoiceResponses

    def __chooseRandomTriviaSource(
        self,
        isLocalTriviaRepositoryEnabled: bool = False
    ) -> TriviaSource:
        if not utils.isValidBool(isLocalTriviaRepositoryEnabled):
            raise ValueError(f'isLocalTriviaRepositoryEnabled argument is malformed: \"{isLocalTriviaRepositoryEnabled}\"')

        triviaSourcesAndWeights = self.__getAvailableTriviaSourcesAndWeights(isLocalTriviaRepositoryEnabled)
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
        print(f'Fetching trivia question from Bongo... ({utils.getNowTimeText(includeSeconds = True)})')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://beta-trivia.bongo.best/?limit=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch trivia from Bongo: {e}')
            return None

        jsonResponse: List[Dict[str, object]] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Bongo\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Bongo\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            print(f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')

        triviaJson: Dict[str, object] = jsonResponse[0]

        if not utils.hasItems(triviaJson):
            print(f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Bongo\'s API data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(triviaJson.get('difficulty'))
        triviaType = TriviaType.fromStr(utils.getStrFromDict(triviaJson, 'type'))
        category = utils.getStrFromDict(triviaJson, 'category', fallback = '', clean = True, htmlUnescape = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True, htmlUnescape = True)
        triviaId = utils.getStrFromDict(triviaJson, 'id')

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
                correctAnswer = correctAnswer,
                multipleChoiceResponsesJson = triviaJson['incorrect_answers']
            )

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
        print(f'Fetching trivia question from jService... ({utils.getNowTimeText(includeSeconds = True)})')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://jservice.io/api/random',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch trivia from jService: {e}')
            return None

        jsonResponse: List[Dict[str, object]] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode jService\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode jService\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            print(f'Rejecting jService data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService data due to null/empty contents: {jsonResponse}')

        resultJson: Dict[str, object] = jsonResponse[0]

        if not utils.hasItems(resultJson):
            print(f'Rejecting jService data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService data due to null/empty contents: {jsonResponse}')

        category = utils.getStrFromDict(resultJson['category'], 'title', fallback = '', clean = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True)
        triviaId = utils.getStrFromDict(resultJson, 'id')

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

    def __fetchTriviaQuestionFromLocalTriviaRepository(self) -> AbsTriviaQuestion:
        print(f'Fetching trivia question from LocalTriviaRepository... ({utils.getNowTimeText(includeSeconds = True)})')
        return self.__localTriviaRepository.fetchRandomQuestion()

    def __fetchTriviaQuestionFromOpenTriviaDatabase(self) -> AbsTriviaQuestion:
        print(f'Fetching trivia question from Open Trivia Database... ({utils.getNowTimeText(includeSeconds = True)})')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://opentdb.com/api.php?amount=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch trivia from Open Trivia Database: {e}')
            return None

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            print(f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')
        elif utils.getIntFromDict(jsonResponse, 'response_code', -1) != 0:
            print(f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
        elif not utils.hasItems(jsonResponse.get('results')):
            print(f'Rejecting trivia due to missing/null/empty \"results\" array: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to missing/null/empty \"results\" array: {jsonResponse}')

        resultJson: Dict[str, object] = jsonResponse['results'][0]

        if not utils.hasItems(resultJson):
            print(f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s API data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(resultJson.get('difficulty'))
        triviaType = TriviaType.fromStr(utils.getStrFromDict(resultJson, 'type'))
        category = utils.getStrFromDict(resultJson, 'category', fallback = '', clean = True, htmlUnescape = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True, htmlUnescape = True)

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
                correctAnswer = correctAnswer,
                multipleChoiceResponsesJson = resultJson['incorrect_answers']
            )

            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                question = question,
                triviaId = None,
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
                triviaId = None,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
            )
        else:
            raise ValueError(f'triviaType \"{triviaType}\" is not supported for Open Trivia Database: {jsonResponse}')

    def __fetchTriviaQuestionFromWillFryTriviaApi(self) -> AbsTriviaQuestion:
        print(f'Fetching trivia question from Will Fry Trivia API... ({utils.getNowTimeText(includeSeconds = True)})')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://trivia.willfry.co.uk/api/questions?limit=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch trivia from Will Fry Trivia API: {e}')
            return None

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Will Fry Trivia API\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Will Fry Trivia API\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            print(f'Rejecting Will Fry Trivia API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Will Fry Trivia API data due to null/empty contents: {jsonResponse}')

        resultJson: Dict[str, object] = jsonResponse[0]

        if not utils.hasItems(resultJson):
            print(f'Rejecting Will Fry Trivia API\'s data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Will Fry Trivia API\'s data due to null/empty contents: {jsonResponse}')

        triviaType = TriviaType.fromStr(utils.getStrFromDict(resultJson, 'type'))
        category = utils.getStrFromDict(resultJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True)
        triviaId = utils.getStrFromDict(resultJson, 'id')

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
                correctAnswer = correctAnswer,
                multipleChoiceResponsesJson = resultJson['incorrectAnswers']
            )

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
        isLocalTriviaRepositoryEnabled: bool = False,
        triviaSource: TriviaSource = None
    ) -> AbsTriviaQuestion:
        if not utils.isValidBool(isLocalTriviaRepositoryEnabled):
            raise ValueError(f'isLocalTriviaRepositoryEnabled argument is malformed: \"{isLocalTriviaRepositoryEnabled}\"')

        if self.__cacheTimeDelta is None or self.__cacheTime is None or self.__cacheTime + self.__cacheTimeDelta < datetime.utcnow() or self.__triviaResponse is None:
            self.__triviaResponse = self.__fetchTrivia(
                isLocalTriviaRepositoryEnabled = isLocalTriviaRepositoryEnabled,
                triviaSource = triviaSource
            )
            self.__cacheTime = datetime.utcnow()

        return self.__triviaResponse

    def __fetchTrivia(
        self,
        isLocalTriviaRepositoryEnabled: bool = False,
        triviaSource: TriviaSource = None
    ) -> AbsTriviaQuestion:
        if not utils.isValidBool(isLocalTriviaRepositoryEnabled):
            raise ValueError(f'isLocalTriviaRepositoryEnabled argument is malformed: \"{isLocalTriviaRepositoryEnabled}\"')

        if triviaSource is None:
            triviaSource = self.__chooseRandomTriviaSource(
                isLocalTriviaRepositoryEnabled = isLocalTriviaRepositoryEnabled
            )

        triviaQuestion: AbsTriviaQuestion = None
        retryCount: int = 0
        maxRetryCount: int = self.__getMaxRetryCount()

        while retryCount < maxRetryCount:
            if triviaSource is TriviaSource.BONGO:
                triviaQuestion = self.__fetchTriviaQuestionFromBongo()
            elif triviaSource is TriviaSource.J_SERVICE:
                triviaQuestion = self.__fetchTriviaQuestionFromJService()
            elif triviaSource is TriviaSource.LOCAL_TRIVIA_REPOSITORY:
                triviaQuestion = self.__fetchTriviaQuestionFromLocalTriviaRepository()
            elif triviaSource is TriviaSource.OPEN_TRIVIA_DATABASE:
                triviaQuestion = self.__fetchTriviaQuestionFromOpenTriviaDatabase()
            elif triviaSource is TriviaSource.WILL_FRY_TRIVIA_API:
                triviaQuestion = self.__fetchTriviaQuestionFromWillFryTriviaApi()
            else:
                raise ValueError(f'unknown TriviaSource: \"{triviaSource}\"')

            if self.__verifyGoodTriviaQuestion(triviaQuestion):
                return triviaQuestion
            else:
                retryCount = retryCount + 1

        raise RuntimeError(f'Unable to fetch trivia after {retryCount} attempts (max attempts is {maxRetryCount} ({utils.getNowTimeText(includeSeconds = True)})')

    def __getAvailableTriviaSourcesAndWeights(
        self,
        isLocalTriviaRepositoryEnabled: bool = False
    ) -> Dict[TriviaSource, int]:
        if not utils.isValidBool(isLocalTriviaRepositoryEnabled):
            raise ValueError(f'isLocalTriviaRepositoryEnabled argument is malformed: \"{isLocalTriviaRepositoryEnabled}\"')

        jsonContents = self.__readTriviaRepositoryJson()
        triviaSourcesJson: Dict = jsonContents['trivia_sources']
        triviaSources: Dict[TriviaSource, int] = dict()

        for key in triviaSourcesJson:
            triviaSource = TriviaSource.fromStr(key)

            if triviaSource is TriviaSource.LOCAL_TRIVIA_REPOSITORY and not isLocalTriviaRepositoryEnabled:
                continue

            triviaSourceJson: Dict = triviaSourcesJson[key]

            isEnabled = utils.getBoolFromDict(triviaSourceJson, 'is_enabled')
            if not isEnabled:
                continue

            weight = utils.getIntFromDict(triviaSourceJson, 'weight')
            if weight < 1:
                raise ValueError(f'triviaSource \"{triviaSource}\" has an invalid weight: \"{weight}\"')

            triviaSources[triviaSource] = weight

        if not utils.hasItems(triviaSources):
            raise RuntimeError(f'triviaSources is empty: \"{triviaSources}\"')

        return triviaSources

    def __getMaxMultipleChoiceResponses(self) -> int:
        jsonContents = self.__readTriviaRepositoryJson()
        maxMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'max_multiple_choice_responses', 5)

        if maxMultipleChoiceResponses < 2:
            raise ValueError(f'maxMultipleChoiceResponses is too small: \"{maxMultipleChoiceResponses}\"')

        return maxMultipleChoiceResponses

    def __getMaxRetryCount(self) -> int:
        jsonContents = self.__readTriviaRepositoryJson()
        maxRetryCount = utils.getIntFromDict(jsonContents, 'max_retry_count', 3)

        if maxRetryCount < 2:
            raise ValueError(f'maxRetryCount is too small: \"{maxRetryCount}\"')

        return maxRetryCount

    def __readTriviaRepositoryJson(self) -> Dict:
        if not path.exists(self.__triviaRepositoryFile):
            raise FileNotFoundError(f'Trivia Repository file not found: \"{self.__triviaRepositoryFile}\"')

        with open(self.__triviaRepositoryFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Trivia Repository file: \"{self.__triviaRepositoryFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Trivia Repository file \"{self.__triviaRepositoryFile}\" is empty')

        return jsonContents

    def __verifyGoodTriviaQuestion(self, triviaQuestion: AbsTriviaQuestion) -> bool:
        if triviaQuestion is None:
            return False

        strings: List[str] = list()
        strings.append(triviaQuestion.getQuestion())
        strings.append(triviaQuestion.getPrompt())

        for response in triviaQuestion.getResponses():
            strings.append(response)

        for string in strings:
            if utils.containsUrl(string):
                return False

        return True
