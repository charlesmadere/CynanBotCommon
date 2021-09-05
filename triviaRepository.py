import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import List

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.localTriviaRepository import LocalTriviaRepository
    from CynanBotCommon.triviaModels import (AbsTriviaQuestion,
                                             MultipleChoiceTriviaQuestion,
                                             QuestionAnswerTriviaQuestion,
                                             TriviaDifficulty, TriviaSource,
                                             TriviaType,
                                             TrueFalseTriviaQuestion)
except:
    import utils
    from localTriviaRepository import LocalTriviaRepository
    from triviaModels import (AbsTriviaQuestion, MultipleChoiceTriviaQuestion,
                              QuestionAnswerTriviaQuestion, TriviaDifficulty,
                              TriviaSource, TriviaType,
                              TrueFalseTriviaQuestion)


class TriviaRepository():

    def __init__(
        self,
        localTriviaRepository: LocalTriviaRepository,
        maxMultipleChoiceResponses: int = 5,
        triviaRepositorySettingsFile: str = 'CynanBotCommon/triviaRepositorySettings.json',
        cacheTimeDelta: timedelta = timedelta(minutes = 2, seconds = 30)
    ):
        if localTriviaRepository is None:
            raise ValueError(f'localTriviaRepository argument is malformed: \"{localTriviaRepository}\"')
        elif not utils.isValidNum(maxMultipleChoiceResponses):
            raise ValueError(f'maxMultipleChoiceResponses argument is malformed: \"{maxMultipleChoiceResponses}\"')
        elif maxMultipleChoiceResponses < 3 or maxMultipleChoiceResponses > 6:
            raise ValueError(f'maxMultipleChoiceResponses argument is out of bounds: \"{maxMultipleChoiceResponses}\"')
        elif not utils.isValidStr(triviaRepositorySettingsFile):
            raise ValueError(f'twitchRepositorySettingsFile argument is malformed: \"{triviaRepositorySettingsFile}\"')

        self.__localTriviaRepository: LocalTriviaRepository = localTriviaRepository
        self.__maxMultipleChoiceResponses: int = maxMultipleChoiceResponses
        self.__triviaRepositorySettingsFile: str = triviaRepositorySettingsFile

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

        multipleChoiceResponses: List[str] = list()
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

                if len(multipleChoiceResponses) >= self.__maxMultipleChoiceResponses:
                    break

        if len(multipleChoiceResponses) < 3:
            raise ValueError(f'This trivia question doesn\'t have enough multiple choice responses: \"{multipleChoiceResponses}\"')

        random.shuffle(multipleChoiceResponses)
        return multipleChoiceResponses

    def __fetchTriviaQuestionFromJService(self, triviaType: TriviaType = None) -> AbsTriviaQuestion:
        print(f'Fetching trivia question from jService... ({utils.getNowTimeText()})')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://jservice.io/api/random',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch trivia from jService: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch trivia from jService: {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode jService\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode jService\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            print(f'Rejecting jService data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService data due to null/empty contents: {jsonResponse}')

        resultJson = jsonResponse[0]
        category = utils.getStrFromDict(resultJson['category'], 'title', fallback = '', clean = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True)

        correctAnswer = utils.getStrFromDict(resultJson, 'answer', clean = True)
        correctAnswers: List[str] = list()
        correctAnswers.append(correctAnswer)

        return QuestionAnswerTriviaQuestion(
            correctAnswers = correctAnswers,
            category = category,
            question = question,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.J_SERVICE
        )

    def __fetchTriviaQuestionFromLocalTriviaRepository(self, triviaType: TriviaType = None) -> AbsTriviaQuestion:
        print(f'Fetching trivia question from LocalTriviaRepository... ({utils.getNowTimeText()})')
        return self.__localTriviaRepository.fetchRandomQuestion()

    def __fetchTriviaQuestionFromOpenTriviaDatabase(self, triviaType: TriviaType = None) -> AbsTriviaQuestion:
        print(f'Fetching trivia question from Open Trivia Database... ({utils.getNowTimeText()})')

        apiUrl = 'https://opentdb.com/api.php?amount=1'
        if triviaType is TriviaType.MULTIPLE_CHOICE:
            apiUrl = f'{apiUrl}&type=multiple'
        elif triviaType is TriviaType.TRUE_FALSE:
            apiUrl = f'{apiUrl}&type=boolean'

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = apiUrl,
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch trivia from Open Trivia Database: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch trivia from Open Trivia Database: {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Trivia Database\'s response into JSON: {e}')

        if utils.getIntFromDict(jsonResponse, 'response_code', -1) != 0:
            print(f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
        elif not utils.hasItems(jsonResponse.get('results')):
            print(f'Rejecting trivia due to null/empty \"results\" array: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to null/empty \"results\" array: {jsonResponse}')

        resultJson = jsonResponse['results'][0]
        triviaDifficulty = TriviaDifficulty.fromStr(resultJson['difficulty'])
        triviaType = TriviaType.fromStr(resultJson['type'])
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
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
            )
        else:
            raise ValueError(f'triviaType \"{triviaType}\" is unknown for Open Trivia Database: {jsonResponse}')

    def __fetchTriviaQuestionFromWillFryTriviaApi(self, triviaType: TriviaType = None) -> AbsTriviaQuestion:
        print(f'Fetching trivia question from Will Fry Trivia API... ({utils.getNowTimeText()})')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://trivia.willfry.co.uk/api/questions?limit=1',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch trivia from Will Fry Trivia API: {e}')
            # This API seems flaky... Let's fallback to a known good one if there's an error.
            return self.__fetchTriviaQuestionFromOpenTriviaDatabase(triviaType)

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Will Fry Trivia API\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Will Fry Trivia API\'s response into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            print(f'Rejecting Will Fry Trivia API data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Will Fry Trivia API data due to null/empty contents: {jsonResponse}')

        resultJson = jsonResponse[0]
        triviaType = TriviaType.fromStr(resultJson['type'])
        category = utils.getStrFromDict(resultJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True)

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
                triviaDifficulty = TriviaDifficulty.UNKNOWN,
                triviaSource = TriviaSource.WILL_FRY_TRIVIA_API
            )
        else:
            raise ValueError(f'triviaType \"{triviaType}\" is unknown for Will Fry Trivia API: {jsonResponse}')

    def fetchTrivia(
        self,
        isLocalTriviaRepositoryEnabled: bool = False,
        triviaSource: TriviaSource = None,
        triviaType: TriviaType = None
    ) -> AbsTriviaQuestion:
        if not utils.isValidBool(isLocalTriviaRepositoryEnabled):
            raise ValueError(f'isLocalTriviaRepositoryEnabled argument is malformed: \"{isLocalTriviaRepositoryEnabled}\"')

        if self.__cacheTimeDelta is None or self.__cacheTime is None or self.__cacheTime + self.__cacheTimeDelta < datetime.utcnow() or self.__triviaResponse is None:
            self.__triviaResponse = self.__fetchTrivia(
                isLocalTriviaRepositoryEnabled = isLocalTriviaRepositoryEnabled,
                triviaSource = triviaSource,
                triviaType = triviaType
            )
            self.__cacheTime = datetime.utcnow()

        return self.__triviaResponse

    def __fetchTrivia(
        self,
        isLocalTriviaRepositoryEnabled: bool = False,
        triviaSource: TriviaSource = None,
        triviaType: TriviaType = None
    ) -> AbsTriviaQuestion:
        if not utils.isValidBool(isLocalTriviaRepositoryEnabled):
            raise ValueError(f'isLocalTriviaRepositoryEnabled argument is malformed: \"{isLocalTriviaRepositoryEnabled}\"')

        triviaSources: List[TriviaSource] = list()
        triviaWeights: List[int] = list()

        for triviaSource in TriviaSource:
            append: bool = False

            if triviaSource.isEnabled():
                if triviaSource is TriviaSource.LOCAL_TRIVIA_REPOSITORY:
                    append = isLocalTriviaRepositoryEnabled
                else:
                    append = True

            if append:
                triviaSources.append(triviaSource)
                triviaWeights.append(triviaSource.getOdds())

        if not utils.hasItems(triviaSources):
            raise RuntimeError(f'triviaSources is empty: \"{triviaSources}\"')
        elif not utils.hasItems(triviaWeights):
            raise RuntimeError(f'triviaWeights is empty: \"{triviaWeights}\"')
        elif len(triviaSources) != len(triviaWeights):
            raise RuntimeError(f'len of triviaSources ({len(triviaSources)}) can\'t be different than len of triviaWeights ({len(triviaWeights)})')

        triviaSource = random.choices(triviaSources, triviaWeights)

        if triviaSource is TriviaSource.J_SERVICE:
            return self.__fetchTriviaQuestionFromJService(triviaType)
        elif triviaSource is TriviaSource.LOCAL_TRIVIA_REPOSITORY:
            return self.__fetchTriviaQuestionFromLocalTriviaRepository(triviaType)
        elif triviaSource is TriviaSource.OPEN_TRIVIA_DATABASE:
            return self.__fetchTriviaQuestionFromOpenTriviaDatabase(triviaType)
        elif triviaSource is TriviaSource.WILL_FRY_TRIVIA_API:
            return self.__fetchTriviaQuestionFromWillFryTriviaApi(triviaType)
        else:
            raise ValueError(f'unknown TriviaSource: \"{triviaSource}\"')
