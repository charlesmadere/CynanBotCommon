import random
from typing import Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.bongoTriviaQuestionRepository import \
        BongoTriviaQuestionRepository
    from CynanBotCommon.trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from CynanBotCommon.trivia.jServiceTriviaQuestionRepository import \
        JServiceTriviaQuestionRepository
    from CynanBotCommon.trivia.lotrTriviaQuestionsRepository import \
        LotrTriviaQuestionRepository
    from CynanBotCommon.trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from CynanBotCommon.trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaExceptions import \
        TooManyTriviaFetchAttemptsException
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
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
    from trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from trivia.jServiceTriviaQuestionRepository import \
        JServiceTriviaQuestionRepository
    from trivia.lotrTriviaQuestionsRepository import \
        LotrTriviaQuestionRepository
    from trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaExceptions import TooManyTriviaFetchAttemptsException
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaVerifier import TriviaVerifier
    from trivia.wwtbamTriviaQuestionRepository import \
        WwtbamTriviaQuestionRepository


class TriviaRepository():

    def __init__(
        self,
        bongoTriviaQuestionRepository: BongoTriviaQuestionRepository,
        jokeTriviaQuestionRepository: JokeTriviaQuestionRepository,
        jServiceTriviaQuestionRepository: JServiceTriviaQuestionRepository,
        openTriviaDatabaseTriviaQuestionRepository: OpenTriviaDatabaseTriviaQuestionRepository,
        lotrTriviaQuestionsRepository: LotrTriviaQuestionRepository,
        quizApiTriviaQuestionRepository: Optional[QuizApiTriviaQuestionRepository],
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaVerifier: TriviaVerifier,
        willFryTriviaQuestionRepository: WillFryTriviaQuestionRepository,
        wwtbamTriviaQuestionRepository: WwtbamTriviaQuestionRepository
    ):
        if bongoTriviaQuestionRepository is None:
            raise ValueError(f'bongoTriviaQuestionRepository argument is malformed: \"{bongoTriviaQuestionRepository}\"')
        elif jokeTriviaQuestionRepository is None:
            raise ValueError(f'jokeTriviaQuestionRepository argument is malformed: \"{jokeTriviaQuestionRepository}\"')
        elif jServiceTriviaQuestionRepository is None:
            raise ValueError(f'jServiceTriviaQuestionRepository argument is malformed: \"{jServiceTriviaQuestionRepository}\"')
        elif lotrTriviaQuestionsRepository is None:
            raise ValueError(f'lotrTriviaQuestionsRepository argument is malformed: \"{lotrTriviaQuestionsRepository}\"')
        elif openTriviaDatabaseTriviaQuestionRepository is None:
            raise ValueError(f'openTriviaDatabaseTriviaQuestionRepository argument is malformed: \"{openTriviaDatabaseTriviaQuestionRepository}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif triviaVerifier is None:
            raise ValueError(f'triviaVerifier argument is malformed: \"{triviaVerifier}\"')
        elif willFryTriviaQuestionRepository is None:
            raise ValueError(f'willFryTriviaQuestionRepository argument is malformed: \"{willFryTriviaQuestionRepository}\"')
        elif wwtbamTriviaQuestionRepository is None:
            raise ValueError(f'wwtbamTriviaQuestionRepository argument is malformed: \"{wwtbamTriviaQuestionRepository}\"')

        self.__bongoTriviaQuestionRepository: AbsTriviaQuestionRepository = bongoTriviaQuestionRepository
        self.__jokeTriviaQuestionRepository: AbsTriviaQuestionRepository = jokeTriviaQuestionRepository
        self.__jServiceTriviaQuestionRepository: AbsTriviaQuestionRepository = jServiceTriviaQuestionRepository
        self.__lotrTriviaQuestionsRepository: AbsTriviaQuestionRepository = lotrTriviaQuestionsRepository
        self.__openTriviaDatabaseTriviaQuestionRepository: AbsTriviaQuestionRepository = openTriviaDatabaseTriviaQuestionRepository
        self.__quizApiTriviaQuestionRepository: AbsTriviaQuestionRepository = quizApiTriviaQuestionRepository
        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__triviaVerifier: TriviaVerifier = triviaVerifier
        self.__willFryTriviaQuestionRepository: AbsTriviaQuestionRepository = willFryTriviaQuestionRepository
        self.__wwtbamTriviaQuestionRepository: AbsTriviaQuestionRepository = wwtbamTriviaQuestionRepository

    async def __chooseRandomTriviaSource(
        self,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> TriviaSource:
        if not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        triviaSourcesAndWeights: Dict[TriviaSource, int] = await self.__triviaSettingsRepository.getAvailableTriviaSourcesAndWeights()

        if not isJokeTriviaRepositoryEnabled and TriviaSource.JOKE_TRIVIA_REPOSITORY in triviaSourcesAndWeights:
            del triviaSourcesAndWeights[TriviaSource.JOKE_TRIVIA_REPOSITORY]

        if not await self.__isQuizApiAvailable() and TriviaSource.QUIZ_API in triviaSourcesAndWeights:
            del triviaSourcesAndWeights[TriviaSource.QUIZ_API]

        if not utils.hasItems(triviaSourcesAndWeights):
            raise RuntimeError(f'There are no trivia sources available to be fetched from!')

        triviaSources: List[TriviaSource] = list()
        triviaWeights: List[int] = list()

        for triviaSource in triviaSourcesAndWeights:
            triviaSources.append(triviaSource)
            triviaWeights.append(triviaSourcesAndWeights[triviaSource])

        randomChoices = random.choices(triviaSources, triviaWeights)
        if not utils.hasItems(triviaSources):
            raise RuntimeError(f'Trivia sources returned by random.choices() is malformed: \"{randomChoices}\"')

        return randomChoices[0]

    async def fetchTrivia(
        self,
        twitchChannel: str,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        return await self.__fetchTrivia(
            twitchChannel = twitchChannel,
            isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
        )

    async def __fetchTrivia(
        self,
        twitchChannel: str,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        triviaSource = await self.__chooseRandomTriviaSource(
            isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
        )

        triviaQuestion: AbsTriviaQuestion = None
        retryCount = 0
        maxRetryCount = await self.__triviaSettingsRepository.getMaxRetryCount()
        attemptedTriviaSources: List[TriviaSource] = list()

        while retryCount < maxRetryCount:
            attemptedTriviaSources.append(triviaSource)

            if triviaSource is TriviaSource.BONGO:
                triviaQuestion = await self.__bongoTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.JOKE_TRIVIA_REPOSITORY:
                triviaQuestion = await self.__jokeTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.J_SERVICE:
                triviaQuestion = await self.__jServiceTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.LORD_OF_THE_RINGS:
                triviaQuestion = await self.__lotrTriviaQuestionsRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.OPEN_TRIVIA_DATABASE:
                triviaQuestion = await self.__openTriviaDatabaseTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.QUIZ_API:
                triviaQuestion = await self.__quizApiTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.WILL_FRY_TRIVIA_API:
                triviaQuestion = await self.__willFryTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            elif triviaSource is TriviaSource.WWTBAM:
                triviaQuestion = await self.__wwtbamTriviaQuestionRepository.fetchTriviaQuestion(twitchChannel)
            else:
                raise ValueError(f'unknown TriviaSource: \"{triviaSource}\"')

            if await self.__verifyGoodTriviaQuestion(triviaQuestion, twitchChannel):
                return triviaQuestion
            else:
                triviaSource = await self.__chooseRandomTriviaSource(
                   isJokeTriviaRepositoryEnabled = isJokeTriviaRepositoryEnabled
                )

                retryCount = retryCount + 1

        raise TooManyTriviaFetchAttemptsException(f'Unable to fetch trivia from {attemptedTriviaSources} after {retryCount} attempts (max attempts is {maxRetryCount})')

    async def __isQuizApiAvailable(self) -> bool:
        return self.__quizApiTriviaQuestionRepository is not None

    async def __verifyGoodTriviaQuestion(
        self,
        triviaQuestion: AbsTriviaQuestion,
        twitchChannel: str
    ) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        triviaContentCode = await self.__triviaVerifier.verify(triviaQuestion, twitchChannel)

        if triviaContentCode == TriviaContentCode.OK:
            return True
        else:
            self.__timber.log('TriviaRepository', f'Rejected a trivia question due to content code: {triviaContentCode}')
            return False
