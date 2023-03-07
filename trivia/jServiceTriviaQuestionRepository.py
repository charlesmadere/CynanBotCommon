from typing import Any, Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException)
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from network.exceptions import GenericNetworkException
    from network.networkClientProvider import NetworkClientProvider
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import (GenericTriviaNetworkException,
                                         MalformedTriviaJsonException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class JServiceTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: Timber,
        triviaAnswerCompiler: TriviaAnswerCompiler,
        triviaIdGenerator: TriviaIdGenerator,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        super().__init__(triviaSettingsRepository)

        if not isinstance(networkClientProvider, NetworkClientProvider):
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaAnswerCompiler, TriviaAnswerCompiler):
            raise ValueError(f'triviaAnswerCompiler argument is malformed: \"{triviaAnswerCompiler}\"')
        elif not isinstance(triviaIdGenerator, TriviaIdGenerator):
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif not isinstance(triviaQuestionCompiler, TriviaQuestionCompiler):
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        questions = await self.fetchTriviaQuestions(
            twitchChannel = twitchChannel,
            count = 1
        )

        if not utils.hasItems(questions):
            return None

        return questions[0]

    async def fetchTriviaQuestions(self, twitchChannel: str, count: int) -> List[AbsTriviaQuestion]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidInt(count):
            raise ValueError(f'count argument is malformed: \"{count}\"')
        elif count < 1 or count > 100:
            raise ValueError(f'count argument is out of bounds: {count}')

        self.__timber.log('JServiceTriviaQuestionRepository', f'Fetching trivia question(s)... (twitchChannel={twitchChannel}, count={count})')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(f'https://jservice.io/api/random?count={count}')
        except GenericNetworkException as e:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Encountered network error: {e}', e)
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

        questions: List[AbsTriviaQuestion] = list()

        for triviaJson in jsonResponse:
            if not utils.hasItems(triviaJson) or 'category' not in triviaJson:
                self.__timber.log('JServiceTriviaQuestionRepository', f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')
                raise MalformedTriviaJsonException(f'Rejecting jService\'s JSON data due to null/empty contents: {jsonResponse}')

            category = utils.getStrFromDict(triviaJson['category'], 'title', fallback = '')
            category = await self.__triviaQuestionCompiler.compileCategory(category)

            question = utils.getStrFromDict(triviaJson, 'question')
            question = await self.__triviaQuestionCompiler.compileQuestion(question)

            triviaId = utils.getStrFromDict(triviaJson, 'id', fallback = '')
            if not utils.isValidStr(triviaId):
                triviaId = await self.__triviaIdGenerator.generate(category = category, question = question)

            correctAnswers: List[str] = list()
            correctAnswers.append(utils.getStrFromDict(triviaJson, 'answer'))
            correctAnswers = await self.__triviaQuestionCompiler.compileResponses(correctAnswers)

            cleanedCorrectAnswers: List[str] = list()
            cleanedCorrectAnswers.append(utils.getStrFromDict(triviaJson, 'answer'))
            cleanedCorrectAnswers = await self.__triviaAnswerCompiler.compileTextAnswersList(cleanedCorrectAnswers)

            expandedCorrectAnswers: Set[str] = set()
            for answer in cleanedCorrectAnswers:
                expandedCorrectAnswers.update(await self.__triviaAnswerCompiler.expandNumerals(answer))

            questions.append(QuestionAnswerTriviaQuestion(
                correctAnswers = correctAnswers,
                cleanedCorrectAnswers = list(expandedCorrectAnswers),
                category = category,
                categoryId = None,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = TriviaDifficulty.UNKNOWN,
                triviaSource = TriviaSource.J_SERVICE
            ))

        if not utils.hasItems(questions):
            self.__timber.log('JServiceTriviaQuestionRepository', f'Unable to fetch any trivia questions from jService (twitchChannel={twitchChannel}, count={count}): {questions}')
            return None

        if len(questions) != count:
            self.__timber.log('JServiceTriviaQuestionRepository', f'Requested {count} questions from jService, but only received {len(questions)} (twitchChannel={twitchChannel}): {questions}')

        return questions

    def getSupportedTriviaTypes(self) -> Set[TriviaType]:
        return { TriviaType.QUESTION_ANSWER }

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.J_SERVICE
