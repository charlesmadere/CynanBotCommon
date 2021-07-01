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
except:
    import utils


class TriviaSource(Enum):

    J_SERVICE = auto()
    OPEN_TRIVIA_DATABASE = auto()
    WILL_FRY_TRIVIA_API = auto()

    def isEnabled(self) -> bool:
        if self is TriviaSource.J_SERVICE:
            return False
        elif self is TriviaSource.OPEN_TRIVIA_DATABASE:
            return True
        elif self is TriviaSource.WILL_FRY_TRIVIA_API:
            return True
        else:
            raise RuntimeError(f'unknown TriviaSource: \"{self}\"')


class TriviaType(Enum):

    MULTIPLE_CHOICE = auto()
    QUESTION_ANSWER = auto()
    TRUE_FALSE = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'boolean':
            return TriviaType.TRUE_FALSE
        elif text == 'multiple' or text == 'multiple choice':
            return TriviaType.MULTIPLE_CHOICE
        else:
            raise ValueError(f'unknown TriviaType: \"{text}\"')


class AbsTriviaQuestion(ABC):

    def __init__(
        self,
        category: str,
        question: str,
        triviaType: TriviaType
    ):
        if not utils.isValidStr(question):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif triviaType is None:
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        self.__category: str = category
        self.__question: str = question
        self.__triviaType: TriviaType = triviaType

    def getAnswerReveal(self) -> str:
        return f'🥁 And the answer is: {self.getCorrectAnswer()}'

    def getCategory(self) -> str:
        return self.__category

    @abstractmethod
    def getCorrectAnswer(self) -> str:
        pass

    @abstractmethod
    def getPrompt(self, delimiter: str = ', ') -> str:
        pass

    def getQuestion(self) -> str:
        return self.__question

    @abstractmethod
    def getResponses(self) -> List[str]:
        pass

    def getTriviaType(self) -> TriviaType:
        return self.__triviaType

    def hasCategory(self) -> bool:
        return utils.isValidStr(self.__category)


class MultipleChoiceTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        category: str,
        correctAnswer: str,
        question: str,
        multipleChoiceResponses: List[str]
    ):
        super().__init__(
            category = category,
            question = question,
            triviaType = TriviaType.MULTIPLE_CHOICE
        )

        if not utils.isValidStr(correctAnswer):
            raise ValueError(f'correctAnswer argument is malformed: \"{correctAnswer}\"')
        elif not utils.hasItems(multipleChoiceResponses):
            raise ValueError(f'multipleChoiceResponses argument is malformed: \"{multipleChoiceResponses}\"')

        self.__correctAnswer: str = correctAnswer
        self.__multipleChoiceResponses: List[str] = multipleChoiceResponses

    def getCorrectAnswer(self) -> str:
        return self.__correctAnswer

    def getCorrectAnswerOrdinal(self) -> int:
        index = 0

        for response in self.__multipleChoiceResponses:
            if response == self.__correctAnswer:
                return index
            else:
                index = index + 1

        raise RuntimeError(f'Couldn\'t find correct answer ordinal for \"{self.__correctAnswer}\"!')

    def getPrompt(self, delimiter: str = ' ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        responsesList = list()
        entryChar = 'A'
        for response in self.__multipleChoiceResponses:
            responsesList.append(f'[{entryChar}] {response}')
            entryChar = chr(ord(entryChar) + 1)

        responses = delimiter.join(responsesList)
        return f'{self.getQuestion()} {responses}'

    def getResponses(self) -> List[str]:
        return self.__multipleChoiceResponses


class QuestionAnswerTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        category: str,
        correctAnswer: str,
        question: str
    ):
        super().__init__(
            category = category,
            question = question,
            triviaType = TriviaType.QUESTION_ANSWER
        )

        if not utils.isValidStr(correctAnswer):
            raise ValueError(f'correctAnswer argument is malformed: \"{correctAnswer}\"')

        self.__correctAnswer: str = correctAnswer

    def getCorrectAnswer(self) -> str:
        return self.__correctAnswer

    def getPrompt(self, delimiter: str = None) -> str:
        categoryText = ''
        if self.hasCategory():
            categoryText = f' (category is \"{self.getCategory()}\")'

        return f'Jeopardy format{categoryText} — {self.getQuestion()}'

    def getResponses(self) -> List[str]:
        return list()


class TrueFalseTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswer: bool,
        category: str,
        question: str
    ):
        super().__init__(
            category = category,
            question = question,
            triviaType = TriviaType.TRUE_FALSE
        )

        if not utils.isValidBool(correctAnswer):
            raise ValueError(f'correctAnswer argument is malformed: \"{correctAnswer}\"')

        self.__correctAnswer: bool = correctAnswer

    def getCorrectAnswer(self) -> str:
        return str(self.__correctAnswer).lower()

    def getCorrectAnswerBool(self) -> bool:
        return self.__correctAnswer

    def getPrompt(self, delimiter: str = None) -> str:
        return f'True or false! {self.getQuestion()}'

    def getResponses(self) -> List[str]:
        return [ str(True).lower(), str(False).lower() ]


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
        correctAnswer = utils.getStrFromDict(resultJson, 'answer', clean = True)
        question = utils.getStrFromDict(resultJson, 'question', clean = True)

        return QuestionAnswerTriviaQuestion(
            category = category,
            correctAnswer = correctAnswer,
            question = question
        )

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

            multipleChoiceResponses = list()
            for answer in resultJson['incorrect_answers']:
                multipleChoiceResponses.append(utils.cleanStr(answer, htmlUnescape = True))

            multipleChoiceResponses.append(correctAnswer)
            random.shuffle(multipleChoiceResponses)

            return MultipleChoiceTriviaQuestion(
                category = category,
                correctAnswer = correctAnswer,
                question = question,
                multipleChoiceResponses = multipleChoiceResponses
            )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswer = utils.getBoolFromDict(resultJson, 'correct_answer')

            return TrueFalseTriviaQuestion(
                correctAnswer = correctAnswer,
                category = category,
                question = question
            )
        else:
            raise ValueError(f'triviaType value is unknown: \"{triviaType}\"')

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
            correctAnswer = utils.getStrFromDict(resultJson, 'correctAnswer', clean = True)

            multipleChoiceResponses = list()
            for answer in resultJson['incorrectAnswers']:
                multipleChoiceResponses.append(utils.cleanStr(answer))

            random.shuffle(multipleChoiceResponses)
            if len(multipleChoiceResponses) > 4:
                multipleChoiceResponses = multipleChoiceResponses[0:4]

            multipleChoiceResponses.append(correctAnswer)
            random.shuffle(multipleChoiceResponses)

            return MultipleChoiceTriviaQuestion(
                category = category,
                correctAnswer = correctAnswer,
                question = question,
                multipleChoiceResponses = multipleChoiceResponses
            )
        else:
            raise ValueError(f'triviaType value is unknown: \"{triviaType}\"')

    def fetchTrivia(
        self,
        triviaSource: TriviaSource = None,
        triviaType: TriviaType = None
    ) -> AbsTriviaQuestion:
        if self.__cacheTime + self.__cacheTimeDelta < datetime.utcnow() or self.__triviaResponse is None:
            self.__triviaResponse = self.__fetchTrivia(triviaSource, triviaType)
            self.__cacheTime = datetime.utcnow()

        return self.__triviaResponse

    def __fetchTrivia(
        self,
        triviaSource: TriviaSource = None,
        triviaType: TriviaType = None
    ) -> AbsTriviaQuestion:
        while triviaSource is None or not triviaSource.isEnabled():
            triviaSource = random.choice(list(TriviaSource))

        if triviaSource is TriviaSource.J_SERVICE:
            return self.__fetchTriviaQuestionFromJService(triviaType)
        if triviaSource is TriviaSource.OPEN_TRIVIA_DATABASE:
            return self.__fetchTriviaQuestionFromOpenTriviaDatabase(triviaType)
        elif triviaSource is TriviaSource.WILL_FRY_TRIVIA_API:
            return self.__fetchTriviaQuestionFromWillFryTriviaApi(triviaType)
        else:
            raise ValueError(f'unknown TriviaSource: \"{triviaSource}\"')
