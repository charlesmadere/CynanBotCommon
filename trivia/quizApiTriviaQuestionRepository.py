from asyncio import TimeoutError
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException,
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
    from network.networkClientProvider import NetworkClientProvider
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from trivia.triviaExceptions import (GenericTriviaNetworkException,
                                         MalformedTriviaJsonException,
                                         NoTriviaCorrectAnswersException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class QuizApiTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        quizApiKey: str,
        timber: Timber,
        triviaEmoteGenerator: TriviaEmoteGenerator,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        super().__init__(triviaSettingsRepository)

        if networkClientProvider is None:
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif not utils.isValidStr(quizApiKey):
            raise ValueError(f'quizApiKey argument is malformed: \"{quizApiKey}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaEmoteGenerator is None:
            raise ValueError(f'triviaEmoteGenerator argument is malformed: \"{triviaEmoteGenerator}\"')
        elif triviaIdGenerator is None:
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__quizApiKey: str = quizApiKey
        self.__timber: Timber = timber
        self.__triviaEmoteGenerator: TriviaEmoteGenerator = triviaEmoteGenerator
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        self.__timber.log('QuizApiTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = f'https://quizapi.io/api/v1/questions?apiKey={self.__quizApiKey}&limit=1',
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0' # LOOOOL
                }
            )
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('QuizApiTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        if response.getStatusCode() != 200:
            self.__timber.log('QuizApiTriviaQuestionRepository', f'Encountered non-200 HTTP status code when fetching trivia question: \"{response.getStatusCode()}\"')
            raise GenericTriviaNetworkException(self.getTriviaSource())

        jsonResponse: Optional[List[Dict[str, Any]]] = await response.json()
        await response.close()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('QuizApiTriviaQuestionRepository', f'{jsonResponse}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('QuizApiTriviaQuestionRepository', f'Rejecting Quiz API\'s JSON data due to null/empty contents: {jsonResponse}')
            raise MalformedTriviaJsonException(f'Rejecting Quiz API JSON data due to null/empty contents: {jsonResponse}')

        triviaJson: Optional[Dict[str, Any]] = jsonResponse[0]
        if not utils.hasItems(triviaJson):
            self.__timber.log('QuizApiTriviaQuestionRepository', f'Rejecting Quiz API\'s JSON data due to null/empty contents: {jsonResponse}')
            raise MalformedTriviaJsonException(f'Rejecting Quiz API\'s JSON data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(utils.getStrFromDict(triviaJson, 'difficulty', fallback = ''))
        category = utils.getStrFromDict(triviaJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True)

        # this API seems to only ever give multiple choice, so for now, we're just hardcoding this
        triviaType = TriviaType.MULTIPLE_CHOICE

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = await self.__triviaIdGenerator.generate(
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
            raise MalformedTriviaJsonException(f'Rejecting Quiz API\'s data due to malformed \"answers\" and/or \"correct_answers\" data: {jsonResponse}')

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

        multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = filteredAnswers
        )

        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            if await self._verifyIsActuallyMultipleChoiceQuestion(correctAnswers, multipleChoiceResponses):
                return MultipleChoiceTriviaQuestion(
                    correctAnswers = correctAnswers,
                    multipleChoiceResponses = multipleChoiceResponses,
                    category = category,
                    categoryId = None,
                    emote = emote,
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
                categoryId = None,
                emote = emote,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.QUIZ_API
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Quiz API: {jsonResponse}')

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE, TriviaType.TRUE_FALSE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.QUIZ_API
