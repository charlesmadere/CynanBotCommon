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

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: Timber = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator

    async def fetchTriviaQuestion(self, twitchChannel: Optional[str]) -> AbsTriviaQuestion:
        self.__timber.log('JServiceTriviaQuestionRepository', 'Fetching trivia question...')

        response = None
        try:
            response = await self.__clientSession.get('https://jservice.io/api/random')
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

        triviaJson: Dict[str, object] = jsonResponse[0]
        if not utils.hasItems(triviaJson) or 'category' not in triviaJson:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

        category = utils.getStrFromDict(triviaJson['category'], 'title', fallback = '', clean = True, removeCarrots = True)
        question = utils.getStrFromDict(triviaJson, 'question', clean = True, removeCarrots = True)

        # this API looks to only ever give question and answer, so for now, we're just hardcoding this
        triviaType = TriviaType.QUESTION_ANSWER

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = await self.__triviaIdGenerator.generate(category = category, question = question)

        if triviaType is TriviaType.QUESTION_ANSWER:
            correctAnswer = utils.getStrFromDict(triviaJson, 'answer', clean = True, removeCarrots = True)
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            return QuestionAnswerTriviaQuestion(
                correctAnswers = correctAnswers,
                cleanedCorrectAnswers = await self.__triviaAnswerCompiler.compileTextAnswers(correctAnswers),
                category = category,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = TriviaDifficulty.UNKNOWN,
                triviaSource = TriviaSource.J_SERVICE
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for jService: {jsonResponse}')

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.QUESTION_ANSWER ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.J_SERVICE
