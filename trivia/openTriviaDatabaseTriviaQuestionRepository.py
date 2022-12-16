from typing import Any, Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
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
        BadTriviaSessionTokenException, GenericTriviaNetworkException,
        UnsupportedTriviaTypeException)
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from network.exceptions import GenericNetworkException
    from network.networkClientProvider import NetworkClientProvider
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from trivia.triviaExceptions import (BadTriviaSessionTokenException,
                                         GenericTriviaNetworkException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class OpenTriviaDatabaseTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: Timber,
        triviaEmoteGenerator: TriviaEmoteGenerator,
        triviaIdGenerator: TriviaIdGenerator,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        super().__init__(triviaSettingsRepository)

        if not isinstance(networkClientProvider, NetworkClientProvider):
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaEmoteGenerator, TriviaEmoteGenerator):
            raise ValueError(f'triviaEmoteGenerator argument is malformed: \"{triviaEmoteGenerator}\"')
        elif not isinstance(triviaIdGenerator, TriviaIdGenerator):
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif not isinstance(triviaQuestionCompiler, TriviaQuestionCompiler):
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber
        self.__triviaEmoteGenerator: TriviaEmoteGenerator = triviaEmoteGenerator
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler

        self.__sessionTokens: Dict[str, str] = dict()

    async def __fetchNewSessionToken(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get('https://opentdb.com/api_token.php?command=request')
        except GenericNetworkException as e:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Encountered network error when fetching Open Trivia Database\'s session token for twitchChannel: \"{twitchChannel}\": {e}', e)
            raise BadTriviaSessionTokenException(f'Encountered network error when fetching Open Trivia Database\'s session token for twitchChannel: \"{twitchChannel}\": {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Encountered non-200 HTTP status code ({response.getStatusCode()}) when fetching Open Trivia Database\'s session token for twitchChannel: \"{twitchChannel}\"')
            raise BadTriviaSessionTokenException(f'Encountered non-200 HTTP status code ({response.getStatusCode()}) when fetching Open Trivia Database\'s session token for twitchChannel: \"{twitchChannel}\"')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'{jsonResponse}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s session token JSON data for twitchChannel \"{twitchChannel}\" due to null/empty JSON contents: {jsonResponse}')
            raise BadTriviaSessionTokenException(f'Rejecting Open Trivia Database\'s session token JSON data for twitchChannel \"{twitchChannel}\" due to null/empty JSON contents: {jsonResponse}')
        elif utils.getIntFromDict(jsonResponse, 'response_code', fallback = -1) != 0:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s session token JSON data for twitchChannel \"{twitchChannel}\" due to bad \"response_code\" value: {jsonResponse}')
            raise BadTriviaSessionTokenException(f'Rejecting Open Trivia Database\'s session token JSON data for twitchChannel \"{twitchChannel}\" due to bad \"response_code\" value: {jsonResponse}')
        elif not utils.isValidStr(jsonResponse.get('token')):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s session token JSON data for twitchChannel \"{twitchChannel}\" due to bad \"token\" value: {jsonResponse}')
            raise BadTriviaSessionTokenException(f'Rejecting Open Trivia Database\'s session token JSON data for twitchChannel \"{twitchChannel}\" due to bad \"token\" value: {jsonResponse}')

        return utils.getStrFromDict(jsonResponse, 'token')

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        sessionToken: Optional[str] = await self.__getOrFetchNewSessionToken(twitchChannel)
        clientSession = await self.__networkClientProvider.get()

        try:
            if utils.isValidStr(sessionToken):
                response = await clientSession.get(f'https://opentdb.com/api.php?amount=1&token={sessionToken}')
            else:
                response = await clientSession.get('https://opentdb.com/api.php?amount=1')
        except GenericNetworkException as e:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        if response.getStatusCode() != 200:
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Encountered non-200 HTTP status code when fetching trivia question: \"{response.getStatusCode()}\"')
            raise GenericTriviaNetworkException(self.getTriviaSource())

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'{jsonResponse}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s JSON data due to null/empty JSON contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s JSON data due to null/empty JSON contents: {jsonResponse}')
        elif utils.getIntFromDict(jsonResponse, 'response_code', fallback = -1) != 0:
            await self.__removeSessionToken(twitchChannel)
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s JSON data due to bad \"response_code\" value: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s JSON data due to bad \"response_code\" value: {jsonResponse}')
        elif not utils.hasItems(jsonResponse.get('results')):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s JSON data due to missing/null/empty \"results\" array: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s JSON data due to missing/null/empty \"results\" array: {jsonResponse}')

        triviaJson: Dict[str, Any] = jsonResponse['results'][0]
        if not utils.hasItems(triviaJson):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Rejecting Open Trivia Database\'s JSON data due to null/empty \"results\" contents: {jsonResponse}')
            raise ValueError(f'Rejecting Open Trivia Database\'s JSON API data due to null/empty contents: {jsonResponse}')

        triviaDifficulty = TriviaDifficulty.fromStr(utils.getStrFromDict(triviaJson, 'difficulty', fallback = ''))
        triviaType = TriviaType.fromStr(utils.getStrFromDict(triviaJson, 'type'))

        category = await self.__triviaQuestionCompiler.compileQuestion(
            question = utils.getStrFromDict(triviaJson, 'category', fallback = ''),
            htmlUnescape = True
        )

        question = await self.__triviaQuestionCompiler.compileQuestion(
            question = utils.getStrFromDict(triviaJson, 'question'),
            htmlUnescape = True
        )

        triviaId = await self.__triviaIdGenerator.generate(
            category = category,
            difficulty = triviaDifficulty.toStr(),
            question = question
        )

        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswer = await self.__triviaQuestionCompiler.compileResponse(
                response = utils.getStrFromDict(triviaJson, 'correct_answer'),
                htmlUnescape = True
            )
            correctAnswers: List[str] = list()
            correctAnswers.append(correctAnswer)

            incorrectAnswers = await self.__triviaQuestionCompiler.compileResponses(
                responses = triviaJson['incorrect_answers'],
                htmlUnescape = True
            )

            multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = incorrectAnswers
            )

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
                    triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
                )
            else:
                self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', 'Encountered a multiple choice question that is better suited for true/false')
                triviaType = TriviaType.TRUE_FALSE

        if triviaType is TriviaType.TRUE_FALSE:
            correctAnswer = utils.getBoolFromDict(triviaJson, 'correct_answer')
            correctAnswers: List[bool] = list()
            correctAnswers.append(correctAnswer)

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                categoryId = None,
                emote = emote,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Open Trivia Database: {jsonResponse}')

    async def __getOrFetchNewSessionToken(self, twitchChannel: str) -> Optional[str]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        sessionToken: Optional[str] = self.__sessionTokens.get(twitchChannel.lower())

        if not utils.isValidStr(sessionToken):
            self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Fetching new session token for \"{twitchChannel}\"...')

            try:
                sessionToken = await self.__fetchNewSessionToken(twitchChannel)
                self.__timber.log('OpenTriviaDatabaseTriviaQuestionRepository', f'Fetched new session token for \"{twitchChannel}\": \"{sessionToken}\"')
                self.__sessionTokens[twitchChannel.lower()] = sessionToken
            except BadTriviaSessionTokenException:
                await self.__removeSessionToken(twitchChannel)

        return sessionToken

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE, TriviaType.TRUE_FALSE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.OPEN_TRIVIA_DATABASE

    async def __removeSessionToken(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__sessionTokens.pop(twitchChannel.lower(), '')
