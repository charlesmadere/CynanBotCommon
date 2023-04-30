import asyncio
import queue
import random
import traceback
from queue import SimpleQueue
from typing import Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.bongoTriviaQuestionRepository import \
        BongoTriviaQuestionRepository
    from CynanBotCommon.trivia.funtoonTriviaQuestionRepository import \
        FuntoonTriviaQuestionRepository
    from CynanBotCommon.trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from CynanBotCommon.trivia.jServiceTriviaQuestionRepository import \
        JServiceTriviaQuestionRepository
    from CynanBotCommon.trivia.lotrTriviaQuestionsRepository import \
        LotrTriviaQuestionRepository
    from CynanBotCommon.trivia.millionaireTriviaQuestionRepository import \
        MillionaireTriviaQuestionRepository
    from CynanBotCommon.trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from CynanBotCommon.trivia.openTriviaQaTriviaQuestionRepository import \
        OpenTriviaQaTriviaQuestionRepository
    from CynanBotCommon.trivia.pkmnTriviaQuestionRepository import \
        PkmnTriviaQuestionRepository
    from CynanBotCommon.trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaDatabaseTriviaQuestionRepository import \
        TriviaDatabaseTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException,
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException, NoTriviaQuestionException,
        TooManyTriviaFetchAttemptsException)
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaQuestionCompanyTriviaQuestionRepository import \
        TriviaQuestionCompanyTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaSourceInstabilityHelper import \
        TriviaSourceInstabilityHelper
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.triviaVerifier import TriviaVerifier
    from CynanBotCommon.trivia.willFryTriviaQuestionRepository import \
        WillFryTriviaQuestionRepository
    from CynanBotCommon.trivia.wwtbamTriviaQuestionRepository import \
        WwtbamTriviaQuestionRepository
    from CynanBotCommon.twitch.twitchHandleProviderInterface import \
        TwitchHandleProviderInterface
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.funtoonTriviaQuestionRepository import \
        FuntoonTriviaQuestionRepository
    from trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from trivia.jServiceTriviaQuestionRepository import \
        JServiceTriviaQuestionRepository
    from trivia.lotrTriviaQuestionsRepository import \
        LotrTriviaQuestionRepository
    from trivia.millionaireTriviaQuestionRepository import \
        MillionaireTriviaQuestionRepository
    from trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from trivia.openTriviaQaTriviaQuestionRepository import \
        OpenTriviaQaTriviaQuestionRepository
    from trivia.pkmnTriviaQuestionRepository import \
        PkmnTriviaQuestionRepository
    from trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaDatabaseTriviaQuestionRepository import \
        TriviaDatabaseTriviaQuestionRepository
    from trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException,
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException, NoTriviaQuestionException,
        TooManyTriviaFetchAttemptsException)
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaQuestionCompanyTriviaQuestionRepository import \
        TriviaQuestionCompanyTriviaQuestionRepository
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaSourceInstabilityHelper import \
        TriviaSourceInstabilityHelper
    from trivia.triviaType import TriviaType
    from trivia.triviaVerifier import TriviaVerifier
    from trivia.wwtbamTriviaQuestionRepository import \
        WwtbamTriviaQuestionRepository

    from twitch.twitchHandleProviderInterface import \
        TwitchHandleProviderInterface


class TriviaRepository():

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        bongoTriviaQuestionRepository: BongoTriviaQuestionRepository,
        funtoonTriviaQuestionRepository: FuntoonTriviaQuestionRepository,
        jokeTriviaQuestionRepository: Optional[JokeTriviaQuestionRepository],
        jServiceTriviaQuestionRepository: Optional[JServiceTriviaQuestionRepository],
        lotrTriviaQuestionRepository: Optional[LotrTriviaQuestionRepository],
        millionaireTriviaQuestionRepository: MillionaireTriviaQuestionRepository,
        quizApiTriviaQuestionRepository: Optional[QuizApiTriviaQuestionRepository],
        openTriviaDatabaseTriviaQuestionRepository: OpenTriviaDatabaseTriviaQuestionRepository,
        openTriviaQaTriviaQuestionRepository: OpenTriviaQaTriviaQuestionRepository,
        pkmnTriviaQuestionRepository: PkmnTriviaQuestionRepository,
        timber: Timber,
        triviaDatabaseTriviaQuestionRepository: TriviaDatabaseTriviaQuestionRepository,
        triviaQuestionCompanyTriviaQuestionRepository: TriviaQuestionCompanyTriviaQuestionRepository,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaSourceInstabilityHelper: TriviaSourceInstabilityHelper,
        triviaVerifier: TriviaVerifier,
        twitchHandleProviderInterface: TwitchHandleProviderInterface,
        willFryTriviaQuestionRepository: WillFryTriviaQuestionRepository,
        wwtbamTriviaQuestionRepository: WwtbamTriviaQuestionRepository,
        spoolerLoopSleepTimeSeconds: float = 120,
        triviaRetrySleepTimeSeconds: float = 0.25
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(bongoTriviaQuestionRepository, BongoTriviaQuestionRepository):
            raise ValueError(f'bongoTriviaQuestionRepository argument is malformed: \"{bongoTriviaQuestionRepository}\"')
        elif not isinstance(funtoonTriviaQuestionRepository, FuntoonTriviaQuestionRepository):
            raise ValueError(f'funtoonTriviaQuestionRepository argument is malformed: \"{funtoonTriviaQuestionRepository}\"')
        elif jokeTriviaQuestionRepository is not None and not isinstance(jokeTriviaQuestionRepository, JokeTriviaQuestionRepository):
            raise ValueError(f'jokeTriviaQuestionRepository argument is malformed: \"{jokeTriviaQuestionRepository}\"')
        elif jServiceTriviaQuestionRepository is not None and not isinstance(jServiceTriviaQuestionRepository, JServiceTriviaQuestionRepository):
            raise ValueError(f'jServiceTriviaQuestionRepository argument is malformed \"{jServiceTriviaQuestionRepository}\"')
        elif lotrTriviaQuestionRepository is not None and not isinstance(lotrTriviaQuestionRepository, LotrTriviaQuestionRepository):
            raise ValueError(f'lotrTriviaQuestionRepository argument is malformed: \"{lotrTriviaQuestionRepository}\"')
        elif not isinstance(millionaireTriviaQuestionRepository, MillionaireTriviaQuestionRepository):
            raise ValueError(f'millionaireTriviaQuestionRepository argument is malformed: \"{millionaireTriviaQuestionRepository}\"')
        elif not isinstance(openTriviaDatabaseTriviaQuestionRepository, OpenTriviaDatabaseTriviaQuestionRepository):
            raise ValueError(f'openTriviaDatabaseTriviaQuestionRepository argument is malformed: \"{openTriviaDatabaseTriviaQuestionRepository}\"')
        elif not isinstance(openTriviaQaTriviaQuestionRepository, OpenTriviaQaTriviaQuestionRepository):
            raise ValueError(f'openTriviaQaTriviaQuestionRepository argument is malformed: \"{openTriviaQaTriviaQuestionRepository}\"')
        elif not isinstance(pkmnTriviaQuestionRepository, PkmnTriviaQuestionRepository):
            raise ValueError(f'pkmnTriviaQuestionRepository argument is malformed: \"{pkmnTriviaQuestionRepository}\"')
        elif quizApiTriviaQuestionRepository is not None and not isinstance(quizApiTriviaQuestionRepository, QuizApiTriviaQuestionRepository):
            raise ValueError(f'quizApiTriviaQuestionRepository argument is malformed: \"{quizApiTriviaQuestionRepository}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaDatabaseTriviaQuestionRepository, TriviaDatabaseTriviaQuestionRepository):
            raise ValueError(f'triviaDatabaseTriviaQuestionRepository argument is malformed: \"{triviaDatabaseTriviaQuestionRepository}\"')
        elif not isinstance(triviaQuestionCompanyTriviaQuestionRepository, TriviaQuestionCompanyTriviaQuestionRepository):
            raise ValueError(f'triviaQuestionCompanyTriviaQuestionRepository argument is malformed: \"{triviaQuestionCompanyTriviaQuestionRepository}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not isinstance(triviaSourceInstabilityHelper, TriviaSourceInstabilityHelper):
            raise ValueError(f'triviaSourceInstabilityHelper argument is malformed: \"{triviaSourceInstabilityHelper}\"')
        elif not isinstance(triviaVerifier, TriviaVerifier):
            raise ValueError(f'triviaVerifier argument is malformed: \"{triviaVerifier}\"')
        elif not isinstance(twitchHandleProviderInterface, TwitchHandleProviderInterface):
            raise ValueError(f'twitchHandleProviderInterface argument is malformed: \"{twitchHandleProviderInterface}\"')
        elif not isinstance(willFryTriviaQuestionRepository, WillFryTriviaQuestionRepository):
            raise ValueError(f'willFryTriviaQuestionRepository argument is malformed: \"{willFryTriviaQuestionRepository}\"')
        elif not isinstance(wwtbamTriviaQuestionRepository, WwtbamTriviaQuestionRepository):
            raise ValueError(f'wwtbamTriviaQuestionRepository argument is malformed: \"{wwtbamTriviaQuestionRepository}\"')
        elif not utils.isValidNum(spoolerLoopSleepTimeSeconds):
            raise ValueError(f'spoolerLoopSleepTimeSeconds argument is malformed: \"{spoolerLoopSleepTimeSeconds}\"')
        elif spoolerLoopSleepTimeSeconds < 15 or spoolerLoopSleepTimeSeconds > 300:
            raise ValueError(f'spoolerLoopSleepTimeSeconds argument is out of bounds: {spoolerLoopSleepTimeSeconds}')
        elif not utils.isValidNum(triviaRetrySleepTimeSeconds):
            raise ValueError(f'triviaRetrySleepTimeSeconds argument is malformed: \"{triviaRetrySleepTimeSeconds}\"')
        elif triviaRetrySleepTimeSeconds < 0.25 or triviaRetrySleepTimeSeconds > 3:
            raise ValueError(f'triviaRetrySleepTimeSeconds argument is out of bounds: {triviaRetrySleepTimeSeconds}')

        self.__bongoTriviaQuestionRepository: AbsTriviaQuestionRepository = bongoTriviaQuestionRepository
        self.__funtoonTriviaQuestionRepository: AbsTriviaQuestionRepository = funtoonTriviaQuestionRepository
        self.__jokeTriviaQuestionRepository: Optional[AbsTriviaQuestionRepository] = jokeTriviaQuestionRepository
        self.__jServiceTriviaQuestionRepository: Optional[AbsTriviaQuestionRepository] = jServiceTriviaQuestionRepository
        self.__lotrTriviaQuestionRepository: Optional[AbsTriviaQuestionRepository] = lotrTriviaQuestionRepository
        self.__millionaireTriviaQuestionRepository: AbsTriviaQuestionRepository = millionaireTriviaQuestionRepository
        self.__openTriviaDatabaseTriviaQuestionRepository: AbsTriviaQuestionRepository = openTriviaDatabaseTriviaQuestionRepository
        self.__openTriviaQaTriviaQuestionRepository: AbsTriviaQuestionRepository = openTriviaQaTriviaQuestionRepository
        self.__pkmnTriviaQuestionRepository: AbsTriviaQuestionRepository = pkmnTriviaQuestionRepository
        self.__quizApiTriviaQuestionRepository: Optional[AbsTriviaQuestionRepository] = quizApiTriviaQuestionRepository
        self.__timber: Timber = timber
        self.__triviaDatabaseTriviaQuestionRepository: AbsTriviaQuestionRepository = triviaDatabaseTriviaQuestionRepository
        self.__triviaQuestionCompanyTriviaQuestionRepository: AbsTriviaQuestionRepository = triviaQuestionCompanyTriviaQuestionRepository
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__triviaSourceInstabilityHelper: TriviaSourceInstabilityHelper = triviaSourceInstabilityHelper
        self.__triviaVerifier: TriviaVerifier = triviaVerifier
        self.__twitchHandleProviderInterfae: TwitchHandleProviderInterface = twitchHandleProviderInterface
        self.__willFryTriviaQuestionRepository: AbsTriviaQuestionRepository = willFryTriviaQuestionRepository
        self.__wwtbamTriviaQuestionRepository: AbsTriviaQuestionRepository = wwtbamTriviaQuestionRepository
        self.__spoolerLoopSleepTimeSeconds: float = spoolerLoopSleepTimeSeconds
        self.__triviaRetrySleepTimeSeconds: float = triviaRetrySleepTimeSeconds

        self.__triviaSourceToRepositoryMap: Dict[TriviaSource, Optional[AbsTriviaQuestionRepository]] = self.__createTriviaSourceToRepositoryMap()
        self.__superTriviaQuestionSpool: SimpleQueue[QuestionAnswerTriviaQuestion] = SimpleQueue()
        self.__triviaQuestionSpool: SimpleQueue[AbsTriviaQuestion] = SimpleQueue()
        backgroundTaskHelper.createTask(self.__startSpooler())

    async def __chooseRandomTriviaSource(self, triviaFetchOptions: TriviaFetchOptions) -> AbsTriviaQuestionRepository:
        if not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaSourcesAndWeights: Dict[TriviaSource, int] = await self.__triviaSettingsRepository.getAvailableTriviaSourcesAndWeights()
        triviaSourcesToRemove: Set[TriviaSource] = await self.__getCurrentlyInvalidTriviaSources(triviaFetchOptions)

        for triviaSourceToRemove in triviaSourcesToRemove:
            if triviaSourceToRemove in triviaSourcesAndWeights:
                del triviaSourcesAndWeights[triviaSourceToRemove]

        if not utils.hasItems(triviaSourcesAndWeights):
            raise RuntimeError(f'There are no trivia sources available to be fetched from! TriviaFetchOptions are: {triviaFetchOptions}')

        triviaSources: List[TriviaSource] = list()
        triviaWeights: List[int] = list()

        for triviaSource in triviaSourcesAndWeights:
            triviaSources.append(triviaSource)
            triviaWeights.append(triviaSourcesAndWeights[triviaSource])

        randomChoices = random.choices(
            population = triviaSources,
            weights = triviaWeights
        )

        if not utils.hasItems(randomChoices):
            raise RuntimeError(f'TriviaSource list returned by random.choices() is malformed: \"{randomChoices}\"')

        randomlyChosenTriviaSource = randomChoices[0]
        return self.__triviaSourceToRepositoryMap[randomlyChosenTriviaSource]

    def __createTriviaSourceToRepositoryMap(self) -> Dict[TriviaSource, Optional[AbsTriviaQuestionRepository]]:
        triviaSourceToRepositoryMap: Dict[TriviaSource, Optional[AbsTriviaQuestionRepository]] = {
            TriviaSource.BONGO: self.__bongoTriviaQuestionRepository,
            TriviaSource.FUNTOON: self.__funtoonTriviaQuestionRepository,
            TriviaSource.JOKE_TRIVIA_REPOSITORY: self.__jokeTriviaQuestionRepository,
            TriviaSource.J_SERVICE: self.__jServiceTriviaQuestionRepository,
            TriviaSource.LORD_OF_THE_RINGS: self.__lotrTriviaQuestionRepository,
            TriviaSource.MILLIONAIRE: self.__millionaireTriviaQuestionRepository,
            TriviaSource.OPEN_TRIVIA_DATABASE: self.__openTriviaDatabaseTriviaQuestionRepository,
            TriviaSource.OPEN_TRIVIA_QA: self.__openTriviaQaTriviaQuestionRepository,
            TriviaSource.POKE_API: self.__pkmnTriviaQuestionRepository,
            TriviaSource.QUIZ_API: self.__quizApiTriviaQuestionRepository,
            TriviaSource.THE_QUESTION_CO: self.__triviaQuestionCompanyTriviaQuestionRepository,
            TriviaSource.TRIVIA_DATABASE: self.__triviaDatabaseTriviaQuestionRepository,
            TriviaSource.WILL_FRY_TRIVIA: self.__willFryTriviaQuestionRepository,
            TriviaSource.WWTBAM: self.__wwtbamTriviaQuestionRepository
        }

        if len(triviaSourceToRepositoryMap.keys()) != len(TriviaSource):
            raise RuntimeError(f'triviaSourceToRepositoryMap is missing some members of TriviaSource!')

        return triviaSourceToRepositoryMap

    async def fetchTrivia(
        self,
        emote: str,
        triviaFetchOptions: TriviaFetchOptions
    ) -> Optional[AbsTriviaQuestion]:
        if not utils.isValidStr(emote):
            raise ValueError(f'emote argument is malformed: \"{emote}\"')
        elif not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        question: Optional[AbsTriviaQuestion] = None
        retryCount: int = 0
        maxRetryCount = await self.__triviaSettingsRepository.getMaxRetryCount()
        attemptedTriviaSources: List[TriviaSource] = list()

        while retryCount < maxRetryCount:
            question = await self.__retrieveSpooledTriviaQuestion(triviaFetchOptions)

            if question is None:
                triviaQuestionRepository = await self.__chooseRandomTriviaSource(triviaFetchOptions)
                triviaSource = triviaQuestionRepository.getTriviaSource()
                attemptedTriviaSources.append(triviaSource)

                try:
                    question = await triviaQuestionRepository.fetchTriviaQuestion(triviaFetchOptions.getTwitchChannel())
                except (NoTriviaCorrectAnswersException, NoTriviaMultipleChoiceResponsesException, NoTriviaQuestionException) as e:
                    self.__timber.log('TriviaRepository', f'Failed to fetch trivia question due to malformed data (trivia source was \"{triviaSource}\"): {e}', e)
                except GenericTriviaNetworkException as e:
                    errorCount = self.__triviaSourceInstabilityHelper.incrementErrorCount(triviaSource)
                    self.__timber.log('TriviaRepository', f'Encountered network Exception when fetching trivia question (trivia source was \"{triviaSource}\") (new error count is {errorCount}): {e}', e)
                except MalformedTriviaJsonException as e:
                    errorCount = self.__triviaSourceInstabilityHelper.incrementErrorCount(triviaSource)
                    self.__timber.log('TriviaRepository', f'Encountered malformed JSON Exception when fetching trivia question (trivia source was \"{triviaSource}\") (new error count is {errorCount}): {e}', e)
                except Exception as e:
                    errorCount = self.__triviaSourceInstabilityHelper.incrementErrorCount(triviaSource)
                    self.__timber.log('TriviaRepository', f'Encountered unknown Exception when fetching trivia question (trivia source was \"{triviaSource}\") (new error count is {errorCount}): {e}', e, traceback.format_exc())

            if await self.__verifyGoodTriviaQuestion(
                question = question,
                emote = emote,
                triviaFetchOptions = triviaFetchOptions
            ):
                return question

            question = None
            retryCount = retryCount + 1
            await asyncio.sleep(self.__triviaRetrySleepTimeSeconds * float(retryCount))

        raise TooManyTriviaFetchAttemptsException(f'Unable to fetch trivia from {attemptedTriviaSources} after {retryCount} attempts (max attempts is {maxRetryCount})')

    async def __getCurrentlyInvalidTriviaSources(self, triviaFetchOptions: TriviaFetchOptions) -> Set[TriviaSource]:
        if not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        availableTriviaSourcesMap: Dict[TriviaSource, AbsTriviaQuestionRepository] = dict()
        for triviaSource, triviaQuestionRepository in self.__triviaSourceToRepositoryMap.items():
            if triviaQuestionRepository is not None:
                availableTriviaSourcesMap[triviaSource] = triviaQuestionRepository

        currentlyInvalidTriviaSources: Set[TriviaSource] = set()

        if not triviaFetchOptions.areQuestionAnswerTriviaQuestionsEnabled():
            for triviaSource, triviaQuestionRepository in availableTriviaSourcesMap.items():
                if TriviaType.QUESTION_ANSWER in triviaQuestionRepository.getSupportedTriviaTypes():
                    currentlyInvalidTriviaSources.add(triviaSource)

        if not triviaFetchOptions.isJokeTriviaRepositoryEnabled():
            currentlyInvalidTriviaSources.add(TriviaSource.JOKE_TRIVIA_REPOSITORY)

        if triviaFetchOptions.requireQuestionAnswerTriviaQuestion():
            for triviaSource, triviaQuestionRepository in availableTriviaSourcesMap.items():
                if TriviaType.QUESTION_ANSWER not in triviaQuestionRepository.getSupportedTriviaTypes():
                    currentlyInvalidTriviaSources.add(triviaSource)

        if not await self.__isJokeTriviaQuestionRepositoryAvailable():
            currentlyInvalidTriviaSources.add(TriviaSource.JOKE_TRIVIA_REPOSITORY)

        if not await self.__isJServiceTriviaQuestionRepositoryAvailable():
            currentlyInvalidTriviaSources.add(TriviaSource.J_SERVICE)

        if not await self.__isLotrTriviaQuestionRepositoryAvailable():
            currentlyInvalidTriviaSources.add(TriviaSource.LORD_OF_THE_RINGS)

        if not await self.__isQuizApiTriviaQuestionRepositoryAvailable():
            currentlyInvalidTriviaSources.add(TriviaSource.QUIZ_API)

        unstableTriviaSources = await self.__getCurrentlyUnstableTriviaSources()
        currentlyInvalidTriviaSources.update(unstableTriviaSources)

        return currentlyInvalidTriviaSources

    async def __getCurrentlyUnstableTriviaSources(self) -> Set[TriviaSource]:
        instabilityThreshold = await self.__triviaSettingsRepository.getTriviaSourceInstabilityThreshold()
        unstableTriviaSources: Set[TriviaSource] = set()

        for triviaSource in TriviaSource:
            if self.__triviaSourceInstabilityHelper[triviaSource] >= instabilityThreshold:
                unstableTriviaSources.add(triviaSource)

        return unstableTriviaSources

    async def __isJokeTriviaQuestionRepositoryAvailable(self) -> bool:
        return self.__jokeTriviaQuestionRepository is not None

    async def __isJServiceTriviaQuestionRepositoryAvailable(self) -> bool:
        return self.__jServiceTriviaQuestionRepository is not None

    async def __isLotrTriviaQuestionRepositoryAvailable(self) -> bool:
        return self.__lotrTriviaQuestionRepository is not None

    async def __isQuizApiTriviaQuestionRepositoryAvailable(self) -> bool:
        return self.__quizApiTriviaQuestionRepository is not None

    async def __retrieveSpooledTriviaQuestion(
        self,
        triviaFetchOptions: TriviaFetchOptions
    ) -> Optional[AbsTriviaQuestion]:
        if not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        if triviaFetchOptions.requireQuestionAnswerTriviaQuestion():
            if not self.__superTriviaQuestionSpool.empty():
                try:
                    self.__timber.log('TriviaRepository', f'Retrieving spooled super trivia question (current qsize: {self.__superTriviaQuestionSpool.qsize()})')
                    return self.__superTriviaQuestionSpool.get_nowait()
                except queue.Empty as e:
                    self.__timber.log('TriviaRepository', f'Encountered queue.Empty when trying to retrieve a spooled super trivia question', e, traceback.format_exc())
        else:
            if not self.__triviaQuestionSpool.empty():
                try:
                    self.__timber.log('TriviaRepository', f'Retrieving spooled trivia question (current qsize: {self.__triviaQuestionSpool.qsize()})')
                    return self.__triviaQuestionSpool.get_nowait()
                except queue.Empty as e:
                    self.__timber.log('TriviaRepository', f'Encountered queue.Empty when trying to retrieve a spooled trivia question', e, traceback.format_exc())

        return None

    async def __startSpooler(self):
        while True:
            try:
                if self.__triviaQuestionSpool.qsize() < self.__triviaSettingsRepository.getMaxTriviaQuestionSpoolSize():
                    triviaFetchOptions = TriviaFetchOptions(
                        twitchChannel = await self.__twitchHandleProviderInterfae.getTwitchHandle(),
                        isJokeTriviaRepositoryEnabled = False,
                        questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.NOT_ALLOWED
                    )

                    self.__timber.log('TriviaRepository', f'Spooling up a trivia question (current qsize: {self.__triviaQuestionSpool.qsize()})')
                    triviaQuestionRepository = await self.__chooseRandomTriviaSource(triviaFetchOptions)
                    question = await triviaQuestionRepository.fetchTriviaQuestion(triviaFetchOptions.getTwitchChannel())

                    if question.getTriviaType() is TriviaType.QUESTION_ANSWER or isinstance(question, QuestionAnswerTriviaQuestion):
                        self.__timber.log('TriviaRepository', f'Encountered unexpected trivia question type: \"{question}\"')
                    else:
                        self.__triviaQuestionSpool.put(question)
            except Exception as e:
                self.__timber.log('TriviaRepository', f'Encountered unknown Exception when refreshing trivia question spool', e, traceback.format_exc())

            try:
                if self.__superTriviaQuestionSpool.qsize() < self.__triviaSettingsRepository.getMaxSuperTriviaQuestionSpoolSize():
                    triviaFetchOptions = TriviaFetchOptions(
                        twitchChannel = await self.__twitchHandleProviderInterfae.getTwitchHandle(),
                        isJokeTriviaRepositoryEnabled = False,
                        questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
                    )

                    self.__timber.log('TriviaRepository', f'Spooling up a super trivia question (current qsize: {self.__superTriviaQuestionSpool.qsize()})')
                    triviaQuestionRepository = await self.__chooseRandomTriviaSource(triviaFetchOptions)
                    question = await triviaQuestionRepository.fetchTriviaQuestion(triviaFetchOptions.getTwitchChannel())

                    if question.getTriviaType() is TriviaType.QUESTION_ANSWER and isinstance(question, QuestionAnswerTriviaQuestion):
                        self.__superTriviaQuestionSpool.put(question)
                    else:
                        self.__timber.log('TriviaRepository', f'Encountered unexpected super trivia question type: \"{question}\"')
            except Exception as e:
                self.__timber.log('TriviaRepository', f'Encountered unknown Exception when refreshing super trivia question spool', e, traceback.format_exc())

            await asyncio.sleep(self.__spoolerLoopSleepTimeSeconds)

    async def __verifyGoodTriviaQuestion(
        self,
        question: Optional[AbsTriviaQuestion],
        emote: str,
        triviaFetchOptions: TriviaFetchOptions
    ) -> bool:
        if question is not None and not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidStr(emote):
            raise ValueError(f'emote argument is malformed: \"{emote}\"')
        elif not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaContentCode = await self.__triviaVerifier.verify(
            question = question,
            emote = emote,
            triviaFetchOptions = triviaFetchOptions
        )

        if triviaContentCode == TriviaContentCode.OK:
            return True
        else:
            self.__timber.log('TriviaRepository', f'Rejected a trivia question due to content code: {triviaContentCode}')
            return False
