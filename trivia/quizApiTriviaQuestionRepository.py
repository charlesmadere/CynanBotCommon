from json.decoder import JSONDecodeError
from typing import Dict, List, Tuple

import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import (
        NoTriviaCorrectAnswersException, UnsupportedTriviaTypeException)
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
    from trivia.triviaExceptions import (NoTriviaCorrectAnswersException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class QuizApiTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        quizApiKey: str,
        timber: Timber,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        super().__init__(triviaIdGenerator, triviaSettingsRepository)

        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif not utils.isValidStr(quizApiKey):
            raise ValueError(f'quizApiKey argument is malformed: \"{quizApiKey}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__quizApiKey: str = quizApiKey
        self.__timber: Timber = timber

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        self.__timber.log('QuizApiTriviaQuestionRepository', 'Fetching trivia question...')

        response = await self.__clientSession.get(
            url = f'https://quizapi.io/api/v1/questions?apiKey={self.__quizApiKey}&limit=1',
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0' # LOOOOL
            }
        )

        if response.status != 200:
            self.__timber.log('QuizApiTriviaQuestionRepository', f'Encountered non-200 HTTP status code: \"{response.status}\"')
            return None

        jsonResponse: Dict[str, object] = await response.json()
        response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('QuizApiTriviaQuestionRepository', f'Rejecting Quiz API\'s JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Quiz API JSON data due to null/empty contents: {jsonResponse}')

        triviaJson: Dict[str, object] = jsonResponse[0]
        if not utils.hasItems(triviaJson):
            self.__timber.log('QuizApiTriviaQuestionRepository', f'Rejecting Quiz API\'s JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Quiz API\'s JSON data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(utils.getStrFromDict(triviaJson, 'difficulty', fallback = ''))
        category = utils.getStrFromDict(triviaJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True)

        # this API seems to only ever give multiple choice, so for now, we're just hardcoding this
        triviaType = TriviaType.MULTIPLE_CHOICE

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = self._triviaIdGenerator.generate(
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
            raise NoTriviaCorrectAnswersException(f'Rejecting Quiz API\'s JSON data due to there being no correct answers: {jsonResponse}')

        multipleChoiceResponses = self._buildMultipleChoiceResponsesList(
            correctAnswers = correctAnswers,
            multipleChoiceResponsesJson = filteredAnswers
        )

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            if self._verifyIsActuallyMultipleChoiceQuestion(correctAnswers, multipleChoiceResponses):
                return MultipleChoiceTriviaQuestion(
                    correctAnswers = correctAnswers,
                    multipleChoiceResponses = multipleChoiceResponses,
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = triviaDifficulty,
                    triviaSource = TriviaSource.QUIZ_API
                )
            else:
                self.__timber.log('QuizApiTriviaQuestionRepository', f'Encountered a multiple choice question that is better suited for true/false')
                triviaType = TriviaType.TRUE_FALSE

        if triviaType is TriviaType.TRUE_FALSE:
            return TrueFalseTriviaQuestion(
                correctAnswers = utils.strsToBools(correctAnswers),
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.QUIZ_API
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Quiz API: {jsonResponse}')
