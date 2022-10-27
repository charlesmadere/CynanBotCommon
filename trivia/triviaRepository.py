import asyncio
import random
from typing import Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
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
    from CynanBotCommon.trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaDatabaseTriviaQuestionRepository import \
        TriviaDatabaseTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaErrorDict import TriviaErrorDict
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException,
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException, NoTriviaQuestionException,
        TooManyTriviaFetchAttemptsException)
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.triviaVerifier import TriviaVerifier
    from CynanBotCommon.trivia.willFryTriviaQuestionRepository import \
        WillFryTriviaQuestionRepository
    from CynanBotCommon.trivia.wwtbamTriviaQuestionRepository import \
        WwtbamTriviaQuestionRepository
except:
    import utils
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
    from trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaDatabaseTriviaQuestionRepository import \
        TriviaDatabaseTriviaQuestionRepository
    from trivia.triviaErrorDict import TriviaErrorDict
    from trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException,
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException, NoTriviaQuestionException,
        TooManyTriviaFetchAttemptsException)
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.triviaVerifier import TriviaVerifier
    from trivia.wwtbamTriviaQuestionRepository import \
        WwtbamTriviaQuestionRepository


class TriviaRepository():

    def __init__(
        self,
        bongoTriviaQuestionRepository: BongoTriviaQuestionRepository,
        funtoonTriviaQuestionRepository: FuntoonTriviaQuestionRepository,
        jokeTriviaQuestionRepository: Optional[JokeTriviaQuestionRepository],
        jServiceTriviaQuestionRepository: JServiceTriviaQuestionRepository,
        lotrTriviaQuestionRepository: Optional[LotrTriviaQuestionRepository],
        millionaireTriviaQuestionRepository: MillionaireTriviaQuestionRepository,
        quizApiTriviaQuestionRepository: Optional[QuizApiTriviaQuestionRepository],
        openTriviaDatabaseTriviaQuestionRepository: OpenTriviaDatabaseTriviaQuestionRepository,
        openTriviaQaTriviaQuestionRepository: OpenTriviaQaTriviaQuestionRepository,
        timber: Timber,
        triviaDatabaseTriviaQuestionRepository: TriviaDatabaseTriviaQuestionRepository,
        triviaSourceInstabilityDict: TriviaErrorDict,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaVerifier: TriviaVerifier,
        willFryTriviaQuestionRepository: WillFryTriviaQuestionRepository,
        wwtbamTriviaQuestionRepository: WwtbamTriviaQuestionRepository,
        sleepTimeSeconds: float = 0.25
    ):
        if bongoTriviaQuestionRepository is None:
            raise ValueError(f'bongoTriviaQuestionRepository argument is malformed: \"{bongoTriviaQuestionRepository}\"')
        elif funtoonTriviaQuestionRepository is None:
            raise ValueError(f'funtoonTriviaQuestionRepository argument is malformed: \"{funtoonTriviaQuestionRepository}\"')
        elif jServiceTriviaQuestionRepository is None:
            raise ValueError(f'jServiceTriviaQuestionRepository argument is malformed: \"{jServiceTriviaQuestionRepository}\"')
        elif millionaireTriviaQuestionRepository is None:
            raise ValueError(f'millionaireTriviaQuestionRepository argument is malformed: \"{millionaireTriviaQuestionRepository}\"')
        elif openTriviaDatabaseTriviaQuestionRepository is None:
            raise ValueError(f'openTriviaDatabaseTriviaQuestionRepository argument is malformed: \"{openTriviaDatabaseTriviaQuestionRepository}\"')
        elif openTriviaQaTriviaQuestionRepository is None:
            raise ValueError(f'openTriviaQaTriviaQuestionRepository argument is malformed: \"{openTriviaQaTriviaQuestionRepository}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaDatabaseTriviaQuestionRepository is None:
            raise ValueError(f'triviaDatabaseTriviaQuestionRepository argument is malformed: \"{triviaDatabaseTriviaQuestionRepository}\"')
        elif triviaSourceInstabilityDict is None:
            raise ValueError(f'triviaSourceInstabilityDict argument is malformed: \"{triviaSourceInstabilityDict}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif triviaVerifier is None:
            raise ValueError(f'triviaVerifier argument is malformed: \"{triviaVerifier}\"')
        elif willFryTriviaQuestionRepository is None:
            raise ValueError(f'willFryTriviaQuestionRepository argument is malformed: \"{willFryTriviaQuestionRepository}\"')
        elif wwtbamTriviaQuestionRepository is None:
            raise ValueError(f'wwtbamTriviaQuestionRepository argument is malformed: \"{wwtbamTriviaQuestionRepository}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 0.1 or sleepTimeSeconds > 3:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')

        self.__bongoTriviaQuestionRepository: AbsTriviaQuestionRepository = bongoTriviaQuestionRepository
        self.__funtoonTriviaQuestionRepository: AbsTriviaQuestionRepository = funtoonTriviaQuestionRepository
        self.__jokeTriviaQuestionRepository: Optional[AbsTriviaQuestionRepository] = jokeTriviaQuestionRepository
        self.__jServiceTriviaQuestionRepository: AbsTriviaQuestionRepository = jServiceTriviaQuestionRepository
        self.__lotrTriviaQuestionRepository: Optional[AbsTriviaQuestionRepository] = lotrTriviaQuestionRepository
        self.__millionaireTriviaQuestionRepository: AbsTriviaQuestionRepository = millionaireTriviaQuestionRepository
        self.__openTriviaDatabaseTriviaQuestionRepository: AbsTriviaQuestionRepository = openTriviaDatabaseTriviaQuestionRepository
        self.__openTriviaQaTriviaQuestionRepository: OpenTriviaQaTriviaQuestionRepository = openTriviaQaTriviaQuestionRepository
        self.__quizApiTriviaQuestionRepository: Optional[AbsTriviaQuestionRepository] = quizApiTriviaQuestionRepository
        self.__timber: Timber = timber
        self.__triviaDatabaseTriviaQuestionRepository: AbsTriviaQuestionRepository = triviaDatabaseTriviaQuestionRepository
        self.__triviaSourceInstabilityDict: TriviaErrorDict = triviaSourceInstabilityDict
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__triviaVerifier: TriviaVerifier = triviaVerifier
        self.__willFryTriviaQuestionRepository: AbsTriviaQuestionRepository = willFryTriviaQuestionRepository
        self.__wwtbamTriviaQuestionRepository: AbsTriviaQuestionRepository = wwtbamTriviaQuestionRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds

        self.__triviaSourceToRepositoryMap: Dict[TriviaSource, AbsTriviaQuestionRepository] = self.__createTriviaSourceToRepositoryMap()

    async def __chooseRandomTriviaSource(self, triviaFetchOptions: TriviaFetchOptions) -> AbsTriviaQuestionRepository:
        if triviaFetchOptions is None:
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

    def __createTriviaSourceToRepositoryMap(self) -> Dict[TriviaSource, AbsTriviaQuestionRepository]:
        triviaSourceToRepositoryMap: Dict[TriviaSource, AbsTriviaQuestionRepository] = {
            TriviaSource.BONGO: self.__bongoTriviaQuestionRepository,
            TriviaSource.FUNTOON: self.__funtoonTriviaQuestionRepository,
            TriviaSource.JOKE_TRIVIA_REPOSITORY: self.__jokeTriviaQuestionRepository,
            TriviaSource.J_SERVICE: self.__jServiceTriviaQuestionRepository,
            TriviaSource.LORD_OF_THE_RINGS: self.__lotrTriviaQuestionRepository,
            TriviaSource.MILLIONAIRE: self.__millionaireTriviaQuestionRepository,
            TriviaSource.OPEN_TRIVIA_DATABASE: self.__openTriviaDatabaseTriviaQuestionRepository,
            TriviaSource.OPEN_TRIVIA_QA: self.__openTriviaQaTriviaQuestionRepository,
            TriviaSource.QUIZ_API: self.__quizApiTriviaQuestionRepository,
            TriviaSource.TRIVIA_DATABASE: self.__triviaDatabaseTriviaQuestionRepository,
            TriviaSource.WILL_FRY_TRIVIA: self.__willFryTriviaQuestionRepository,
            TriviaSource.WWTBAM: self.__wwtbamTriviaQuestionRepository
        }

        if len(triviaSourceToRepositoryMap.keys()) != len(TriviaSource):
            raise RuntimeError(f'triviaSourceToRepositoryMap is missing some members of TriviaSource!')

        return triviaSourceToRepositoryMap

    async def fetchTrivia(self, triviaFetchOptions: TriviaFetchOptions) -> Optional[AbsTriviaQuestion]:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        return await self.__fetchTrivia(triviaFetchOptions)

    async def __fetchTrivia(self, triviaFetchOptions: TriviaFetchOptions) -> Optional[AbsTriviaQuestion]:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaQuestion: Optional[AbsTriviaQuestion] = None
        retryCount: int = 0
        maxRetryCount = await self.__triviaSettingsRepository.getMaxRetryCount()
        attemptedTriviaSources: List[TriviaSource] = list()

        while retryCount < maxRetryCount:
            triviaQuestionRepository = await self.__chooseRandomTriviaSource(triviaFetchOptions)
            triviaSource = triviaQuestionRepository.getTriviaSource()
            attemptedTriviaSources.append(triviaSource)

            try:
                triviaQuestion = await triviaQuestionRepository.fetchTriviaQuestion(triviaFetchOptions.getTwitchChannel())
            except (NoTriviaCorrectAnswersException, NoTriviaMultipleChoiceResponsesException, NoTriviaQuestionException) as e:
                self.__timber.log('TriviaRepository', f'Failed to fetch trivia question due to malformed data (trivia source was \"{triviaSource}\"): {e}')
            except (GenericTriviaNetworkException, MalformedTriviaJsonException) as e:
                errorCount = self.__triviaSourceInstabilityDict.incrementErrorCount(triviaSource)
                self.__timber.log('TriviaRepository', f'Encountered bad API Exception when fetching trivia question (trivia source was \"{triviaSource}\") (new error count is {errorCount}): {e}')
            except Exception as e:
                errorCount = self.__triviaSourceInstabilityDict.incrementErrorCount(triviaSource)
                self.__timber.log('TriviaRepository', f'Encountered unknown Exception when fetching trivia question (trivia source was \"{triviaSource}\") (new error count is {errorCount}): {e}')

            if await self.__verifyGoodTriviaQuestion(triviaQuestion, triviaFetchOptions):
                return triviaQuestion

            retryCount = retryCount + 1
            await asyncio.sleep(self.__sleepTimeSeconds * float(retryCount))

        raise TooManyTriviaFetchAttemptsException(f'Unable to fetch trivia from {attemptedTriviaSources} after {retryCount} attempts (max attempts is {maxRetryCount})')

    async def __getCurrentlyInvalidTriviaSources(self, triviaFetchOptions: TriviaFetchOptions) -> Set[TriviaSource]:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        currentlyInvalidTriviaSources: Set[TriviaSource] = set()

        if not triviaFetchOptions.areQuestionAnswerTriviaQuestionsEnabled():
            for triviaSource, triviaQuestionRepository in self.__triviaSourceToRepositoryMap.items():
                if TriviaType.QUESTION_ANSWER in triviaQuestionRepository.getSupportedTriviaTypes():
                    currentlyInvalidTriviaSources.add(triviaSource)

        if not triviaFetchOptions.isJokeTriviaRepositoryEnabled():
            currentlyInvalidTriviaSources.add(TriviaSource.JOKE_TRIVIA_REPOSITORY)

        if triviaFetchOptions.requireQuestionAnswerTriviaQuestion():
            for triviaSource, triviaQuestionRepository in self.__triviaSourceToRepositoryMap.items():
                if TriviaType.QUESTION_ANSWER not in triviaQuestionRepository.getSupportedTriviaTypes():
                    currentlyInvalidTriviaSources.add(triviaSource)

        if not await self.__isJokeTriviaQuestionRepositoryAvailable():
            currentlyInvalidTriviaSources.add(TriviaSource.JOKE_TRIVIA_REPOSITORY)

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
            if self.__triviaSourceInstabilityDict[triviaSource] >= instabilityThreshold:
                unstableTriviaSources.add(triviaSource)

        return unstableTriviaSources

    async def __isJokeTriviaQuestionRepositoryAvailable(self) -> bool:
        return self.__jokeTriviaQuestionRepository is not None

    async def __isLotrTriviaQuestionRepositoryAvailable(self) -> bool:
        return self.__lotrTriviaQuestionRepository is not None

    async def __isQuizApiTriviaQuestionRepositoryAvailable(self) -> bool:
        return self.__quizApiTriviaQuestionRepository is not None

    async def __verifyGoodTriviaQuestion(
        self,
        triviaQuestion: AbsTriviaQuestion,
        triviaFetchOptions: TriviaFetchOptions
    ) -> bool:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaContentCode = await self.__triviaVerifier.verify(triviaQuestion, triviaFetchOptions)

        if triviaContentCode == TriviaContentCode.OK:
            return True
        else:
            self.__timber.log('TriviaRepository', f'Rejected a trivia question due to content code: {triviaContentCode}')
            return False
