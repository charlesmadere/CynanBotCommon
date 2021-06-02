import html
import random
from datetime import datetime, timedelta
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import List

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaType(Enum):

    ANY = auto()
    MULTIPLE_CHOICE = auto()
    TRUE_FALSE = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        # TriviaType.ANY is intentionally left out of the below if statements

        if text == 'boolean':
            return TriviaType.TRUE_FALSE
        elif text == 'multiple':
            return TriviaType.MULTIPLE_CHOICE
        else:
            raise ValueError(f'unknown TriviaType: \"{text}\"')


class TriviaResponse():

    def __init__(
        self,
        category: str,
        question: str,
        triviaType: TriviaType,
        trueFalseResponses: List[str] = None,
        correctTrueFalseAnswer: bool = None,
        multipleChoiceResponses: List[str] = None,
        correctMultipleChoiceAnswer: str = None
    ):
        if not utils.isValidStr(category):
            raise ValueError(f'category argument is malformed: \"{category}\"')
        elif not utils.isValidStr(question):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif triviaType is None:
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')
        elif triviaType is TriviaType.TRUE_FALSE and not utils.hasItems(trueFalseResponses):
            raise ValueError(f'triviaType is {triviaType} but trueFalseResponses is malformed: \"{trueFalseResponses}\"')
        elif triviaType is TriviaType.TRUE_FALSE and not utils.isValidBool(correctTrueFalseAnswer):
            raise ValueError(f'triviaType is {triviaType} but correctTrueFalseAnswer is malformed: \"{correctTrueFalseAnswer}\"')
        elif triviaType is TriviaType.MULTIPLE_CHOICE and not utils.hasItems(multipleChoiceResponses):
            raise ValueError(f'triviaType is {triviaType} but multipleChoiceResponses is malformed: \"{multipleChoiceResponses}\"')
        elif triviaType is TriviaType.MULTIPLE_CHOICE and not utils.isValidStr(correctMultipleChoiceAnswer):
            raise ValueError(f'triviaType is {triviaType} but correctMultipleChoiceAnswer is malformed: \"{correctMultipleChoiceAnswer}\"')

        self.__category = category
        self.__question = question
        self.__triviaType = triviaType
        self.__trueFalseResponses = trueFalseResponses
        self.__correctTrueFalseAnswer = correctTrueFalseAnswer
        self.__multipleChoiceResponses = multipleChoiceResponses
        self.__correctMultipleChoiceAnswer = correctMultipleChoiceAnswer

    def getCategory(self) -> str:
        return self.__category

    def getCorrectAnswer(self) -> str:
        if self.__triviaType is TriviaType.MULTIPLE_CHOICE:
            return self.__correctMultipleChoiceAnswer
        elif self.__triviaType is TriviaType.TRUE_FALSE:
            return str(self.__correctTrueFalseAnswer)
        else:
            raise RuntimeError(f'triviaType is unknown value: \"{self.__triviaType}\"')

    def getMultipleChoiceResponses(self) -> List[str]:
        if self.__triviaType is TriviaType.MULTIPLE_CHOICE:
            return self.__multipleChoiceResponses
        else:
            raise RuntimeError(f'triviaType is {self.__triviaType}, so multipleChoiceResponses is inaccessible')

    def getQuestion(self) -> str:
        return self.__question

    def getTriviaType(self) -> TriviaType:
        return self.__triviaType

    def getTrueFalseResponses(self) -> List[str]:
        if self.__triviaType is TriviaType.TRUE_FALSE:
            return self.__trueFalseResponses
        else:
            raise RuntimeError(f'triviaType is {self.__triviaType}, so trueFalseResponses is inaccessible')

    def toAnswerStr(self) -> str:
        return f'and the answer is: {self.getCorrectAnswer()}'

    def toPromptStr(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        if self.__triviaType is TriviaType.MULTIPLE_CHOICE:
            responses = delimiter.join(self.__multipleChoiceResponses)
            return f'{self.__question} {responses}'
        elif self.__triviaType is TriviaType.TRUE_FALSE:
            return f'True or false! {self.__question}'
        else:
            raise RuntimeError(f'triviaType is unknown value: \"{self.__triviaType}\"')


class TriviaRepository():

    def __init__(
        self,
        cacheTimeDelta: timedelta = timedelta(minutes = 2, seconds = 30)
    ):
        if cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__cacheTime = datetime.utcnow() - cacheTimeDelta
        self.__cacheTimeDelta = cacheTimeDelta
        self.__triviaResponse = None

    def fetchTrivia(self, triviaType: TriviaType = TriviaType.ANY) -> TriviaResponse:
        if triviaType is None:
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        if self.__cacheTime + self.__cacheTimeDelta < datetime.utcnow() or self.__triviaResponse is None:
            self.__triviaResponse = self.__refreshTrivia(triviaType)
            self.__cacheTime = datetime.utcnow()

        return self.__triviaResponse

    def __refreshTrivia(self, triviaType: TriviaType = TriviaType.ANY) -> TriviaResponse:
        if triviaType is None:
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        print(f'Refreshing trivia... ({utils.getNowTimeText()})')

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
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch new trivia: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch new trivia: {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode trivia\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode trivia\'s response into JSON: {e}')

        if utils.getIntFromDict(jsonResponse, 'response_code', -1) != 0:
            print(f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to bad \"response_code\" value: {jsonResponse}')
        elif not utils.hasItems(jsonResponse.get('results')):
            print(f'Rejecting trivia due to null/empty \"results\" array: {jsonResponse}')
            raise ValueError(f'Rejecting trivia due to null/empty \"results\" array: {jsonResponse}')

        resultJson = jsonResponse['results'][0]
        triviaType = TriviaType.fromStr(resultJson['type'])

        trueFalseResponses = None
        correctTrueFalseAnswer = None
        multipleChoiceResponses = None
        correctMultipleChoiceAnswer = None

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctMultipleChoiceAnswer = html.unescape(utils.cleanStr(resultJson['correct_answer']))

            multipleChoiceResponses = list()
            for answer in resultJson['incorrect_answers']:
                multipleChoiceResponses.append(html.unescape(utils.cleanStr(answer)))

            multipleChoiceResponses.append(correctMultipleChoiceAnswer)
            random.shuffle(multipleChoiceResponses)
        elif triviaType is TriviaType.TRUE_FALSE:
            correctTrueFalseAnswer = utils.getBoolFromDict(resultJson, 'correct_answer')

            trueFalseResponses = list()
            for answer in resultJson['incorrect_answers']:
                trueFalseResponses.append(html.unescape(utils.cleanStr(answer)))

            trueFalseResponses.append(utils.cleanStr(resultJson['correct_answer']))
            random.shuffle(trueFalseResponses)
        else:
            raise ValueError(f'triviaType value is unknown: \"{triviaType}\"')

        return TriviaResponse(
            category = html.unescape(utils.cleanStr(resultJson['category'])),
            question = html.unescape(utils.cleanStr(resultJson['question'])),
            triviaType = triviaType,
            trueFalseResponses = trueFalseResponses,
            correctTrueFalseAnswer = correctTrueFalseAnswer,
            multipleChoiceResponses = multipleChoiceResponses,
            correctMultipleChoiceAnswer = correctMultipleChoiceAnswer
        )
