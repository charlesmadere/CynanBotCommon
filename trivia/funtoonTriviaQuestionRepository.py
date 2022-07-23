from asyncio import TimeoutError
from typing import Any, Dict, List

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
    from CynanBotCommon.trivia.triviaEmoteGenerator import TriviaEmoteGenerator
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
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class FuntoonTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        timber: Timber,
        triviaAnswerCompiler: TriviaAnswerCompiler,
        triviaEmoteGenerator: TriviaEmoteGenerator,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        super().__init__(triviaSettingsRepository)

        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif triviaEmoteGenerator is None:
            raise ValueError(f'triviaEmoteGenerator argument is malformed: \"{triviaEmoteGenerator}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaAnswerCompiler is None:
            raise ValueError(f'triviaAnswerCompiler argument is malformed: \"{triviaAnswerCompiler}\"')
        elif triviaQuestionCompiler is None:
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: Timber = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaEmoteGenerator: TriviaEmoteGenerator = triviaEmoteGenerator
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('FuntoonTriviaQuestionRepository', f'Fetching trivia question(s)... (twitchChannel={twitchChannel})')

        response = None
        try:
            response = await self.__clientSession.get(f'https://funtoon.party/api/trivia/random')
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('FuntoonTriviaQuestionRepository', f'Encountered network error: {e}')
            return None

        if response.status != 200:
            self.__timber.log('FuntoonTriviaQuestionRepository', f'Encountered non-200 HTTP status code: \"{response.status}\"')
            return None

        jsonResponse: List[Dict[str, Any]] = await response.json()
        response.close()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('FuntoonTriviaQuestionRepository', f'{jsonResponse}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('FuntoonTriviaQuestionRepository', f'Rejecting Funtoon\'s JSON data due to null/empty contents: {jsonResponse}')
            raise ValueError(f'Rejecting Funtoon\'s JSON data due to null/empty contents: {jsonResponse}')

        category = utils.getStrFromDict(jsonResponse, 'category', fallback = '')
        category = await self.__triviaQuestionCompiler.compileCategory(category)

        categoryId = utils.getStrFromDict(jsonResponse, 'category_id')

        question = utils.getStrFromDict(jsonResponse, 'clue')
        question = await self.__triviaQuestionCompiler.compileQuestion(question)

        triviaId = utils.getStrFromDict(jsonResponse, 'id')

        correctAnswers: List[str] = list()
        correctAnswers.append(utils.getStrFromDict(jsonResponse, 'answer'))
        correctAnswers = await self.__triviaQuestionCompiler.compileResponses(correctAnswers)

        cleanedCorrectAnswers: List[str] = list()
        cleanedCorrectAnswers.append(utils.getStrFromDict(jsonResponse, 'answer'))
        cleanedCorrectAnswers = await self.__triviaAnswerCompiler.compileTextAnswersList(cleanedCorrectAnswers)

        expandedCorrectAnswers: List[str] = list()
        for answer in cleanedCorrectAnswers:
            expandedCorrectAnswers.extend(await self.__triviaAnswerCompiler.expandNumerals(answer))

        # TODO In the future, we will also check some additional fields (`formatted_answer` and
        # `format_type`). These will assist in providing computer-readable answer logic.

        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)

        return QuestionAnswerTriviaQuestion(
            correctAnswers = correctAnswers,
            cleanedCorrectAnswers = expandedCorrectAnswers,
            category = category,
            categoryId = categoryId,
            emote = emote,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.FUNTOON
        )

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.QUESTION_ANSWER ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.FUNTOON
