import traceback
from typing import Any, Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.additionalTriviaAnswersRepositoryInterface import \
        AdditionalTriviaAnswersRepositoryInterface
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException)
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
    from CynanBotCommon.trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from network.exceptions import GenericNetworkException
    from network.networkClientProvider import NetworkClientProvider
    from timber.timberInterface import TimberInterface
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.additionalTriviaAnswersRepositoryInterface import \
        AdditionalTriviaAnswersRepositoryInterface
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import (GenericTriviaNetworkException,
                                         MalformedTriviaJsonException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class JServiceTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        additionalTriviaAnswersRepository: AdditionalTriviaAnswersRepositoryInterface,
        networkClientProvider: NetworkClientProvider,
        timber: TimberInterface,
        triviaAnswerCompiler: TriviaAnswerCompiler,
        triviaIdGenerator: TriviaIdGenerator,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepositoryInterface
    ):
        super().__init__(triviaSettingsRepository)

        if not isinstance(additionalTriviaAnswersRepository, AdditionalTriviaAnswersRepositoryInterface):
            raise ValueError(f'additionalTriviaAnswersRepository argument is malformed: \"{additionalTriviaAnswersRepository}\"')
        elif not isinstance(networkClientProvider, NetworkClientProvider):
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaAnswerCompiler, TriviaAnswerCompiler):
            raise ValueError(f'triviaAnswerCompiler argument is malformed: \"{triviaAnswerCompiler}\"')
        elif not isinstance(triviaIdGenerator, TriviaIdGenerator):
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif not isinstance(triviaQuestionCompiler, TriviaQuestionCompiler):
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')

        self.__additionalTriviaAnswersRepository: AdditionalTriviaAnswersRepositoryInterface = additionalTriviaAnswersRepository
        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: TimberInterface = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler

    async def __addAdditionalAnswers(self, correctAnswers: List[str], triviaId: str):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')

        reference = await self.__additionalTriviaAnswersRepository.getAdditionalTriviaAnswers(
            triviaId = triviaId,
            triviaSource = TriviaSource.J_SERVICE,
            triviaType = TriviaType.QUESTION_ANSWER
        )

        if reference is None:
            return

        self.__timber.log('JServiceTriviaQuestionRepository', f'Adding additional answers to question (triviaId=\"{triviaId}\"): {reference.getAdditionalAnswers()}')
        correctAnswers.extend(reference.getAdditionalAnswersStrs())

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('JServiceTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(f'https://jservice.io/api/random?count=1')
        except GenericNetworkException as e:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Encountered network error: {e}', e, traceback.format_exc())
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        if response.getStatusCode() != 200:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Encountered non-200 HTTP status code: \"{response.getStatusCode()}\"')
            raise GenericTriviaNetworkException(self.getTriviaSource())

        jsonResponse: Optional[List[Dict[str, Any]]] = await response.json()
        await response.close()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('JServiceTriviaQuestionRepository', f'{jsonResponse}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
            raise MalformedTriviaJsonException(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

        triviaJson: Optional[Dict[str, Any]] = jsonResponse[0]

        if not utils.hasItems(triviaJson) or 'category' not in triviaJson:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
            raise MalformedTriviaJsonException(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

        category = utils.getStrFromDict(triviaJson['category'], 'title', fallback = '').encode('latin1').decode('utf8')
        category = await self.__triviaQuestionCompiler.compileCategory(category)

        question = utils.getStrFromDict(triviaJson, 'question').encode('latin1').decode('utf8')
        question = await self.__triviaQuestionCompiler.compileQuestion(question)

        triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
        if not utils.isValidStr(triviaId):
            triviaId = await self.__triviaIdGenerator.generate(category = category, question = question)

        correctAnswers: List[str] = list()
        correctAnswers.append(utils.getStrFromDict(triviaJson, 'answer').encode('latin1').decode('utf8'))

        await self.__addAdditionalAnswers(
            correctAnswers = correctAnswers,
            triviaId = triviaId
        )

        correctAnswers = await self.__triviaQuestionCompiler.compileResponses(correctAnswers)

        cleanedCorrectAnswers: List[str] = list()
        cleanedCorrectAnswers.append(utils.getStrFromDict(triviaJson, 'answer').encode('latin1').decode('utf8'))
        cleanedCorrectAnswers = await self.__triviaAnswerCompiler.compileTextAnswersList(cleanedCorrectAnswers)

        expandedCleanedCorrectAnswers: Set[str] = set()
        for answer in cleanedCorrectAnswers:
            expandedCleanedCorrectAnswers.update(await self.__triviaAnswerCompiler.expandNumerals(answer))

        return QuestionAnswerTriviaQuestion(
            correctAnswers = correctAnswers,
            cleanedCorrectAnswers = list(expandedCleanedCorrectAnswers),
            category = category,
            categoryId = None,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.J_SERVICE
        )

    def getSupportedTriviaTypes(self) -> Set[TriviaType]:
        return { TriviaType.QUESTION_ANSWER }

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.J_SERVICE

    async def hasQuestionSetAvailable(self) -> bool:
        return True
