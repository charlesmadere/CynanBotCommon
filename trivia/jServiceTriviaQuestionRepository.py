from asyncio import TimeoutError
from typing import Dict, List, Optional

import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import \
        UnsupportedTriviaTypeException
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
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
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import UnsupportedTriviaTypeException
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class JServiceTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        timber: Timber,
        triviaAnswerCompiler: TriviaAnswerCompiler,
        triviaIdGenerator: TriviaIdGenerator,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        super().__init__(triviaSettingsRepository)

        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaAnswerCompiler is None:
            raise ValueError(f'triviaAnswerCompiler argument is malformed: \"{triviaAnswerCompiler}\"')
        elif triviaIdGenerator is None:
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif triviaQuestionCompiler is None:
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: Timber = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler

    async def fetchTriviaQuestion(self, twitchChannel: Optional[str]) -> AbsTriviaQuestion:
        questions = await self.fetchTriviaQuestions(
            twitchChannel = twitchChannel,
            count = 1
        )

        return questions[0]

    async def fetchTriviaQuestions(self, twitchChannel: Optional[str], count: int) -> List[AbsTriviaQuestion]:
        if not utils.isValidNum(count):
            raise ValueError(f'count argument is malformed: \"{count}\"')
        elif count < 1 or count > 100:
            raise ValueError(f'count argument is out of bounds: {count}')

        self.__timber.log('JServiceTriviaQuestionRepository', f'Fetching trivia question(s)... (count={count})')

        response = None
        try:
            response = await self.__clientSession.get(f'https://jservice.io/api/random?count={count}')
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Encountered network error: {e}')
            return None

        if response.status != 200:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Encountered non-200 HTTP status code: \"{response.status}\"')
            return None

        jsonResponse: List[Dict[str, object]] = await response.json()
        response.close()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('JServiceTriviaQuestionRepository', f'{jsonResponse}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

        questions: List[AbsTriviaQuestion] = list()

        for triviaJson in jsonResponse:
            if not utils.hasItems(triviaJson) or 'category' not in triviaJson:
                self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
                raise ValueError(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

            category = utils.getStrFromDict(triviaJson['category'], 'title', fallback = '')
            category = await self.__triviaQuestionCompiler.compileCategory(category)

            question = utils.getStrFromDict(triviaJson, 'question')
            question = await self.__triviaQuestionCompiler.compileQuestion(question)

            # this API looks to only ever give question and answer, so for now, we're just hardcoding this
            triviaType = TriviaType.QUESTION_ANSWER

            triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
            if not utils.isValidStr(triviaId):
                triviaId = await self.__triviaIdGenerator.generate(category = category, question = question)

            if triviaType is TriviaType.QUESTION_ANSWER:
                correctAnswer = await self.__triviaQuestionCompiler.compileResponse(utils.getStrFromDict(triviaJson, 'answer'))
                correctAnswers: List[str] = list()
                correctAnswers.append(correctAnswer)

                cleanedCorrectAnswers = await self.__triviaAnswerCompiler.compileTextAnswersList(correctAnswers)

                expandedCorrectAnswers: List[str] = list()
                for answer in cleanedCorrectAnswers:
                    expandedCorrectAnswers.extend(await self.__triviaAnswerCompiler.expandNumerals(answer))

                questions.append(QuestionAnswerTriviaQuestion(
                    correctAnswers = correctAnswers,
                    cleanedCorrectAnswers = expandedCorrectAnswers,
                    category = category,
                    question = question,
                    triviaId = triviaId,
                    triviaDifficulty = TriviaDifficulty.UNKNOWN,
                    triviaSource = TriviaSource.J_SERVICE
                ))
            else:
                raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for jService: {jsonResponse}')

        if not utils.hasItems(questions):
            self.__timber.log('JServiceTriviaQuestionRepository', f'Unable to fetch any trivia questions from jService (twitchChannel={twitchChannel}, count={count}): {questions}')
            raise ValueError(f'Unable to fetch any trivia questions from jService (twitchChannel={twitchChannel}, count={count}): {questions}')
        elif len(questions) != count:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Requested {count} questions from jService, but only received {len(questions)} (twitchChannel={twitchChannel}): {questions}')

        return questions

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.QUESTION_ANSWER ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.J_SERVICE
