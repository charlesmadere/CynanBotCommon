import asyncio
import queue
import traceback
from queue import SimpleQueue
from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaRepository import TriviaRepository
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaRepository import TriviaRepository
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class TriviaQuestionSpooler():

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        timber: Timber,
        triviaRepository: TriviaRepository,
        triviaSettingsRepository: TriviaSettingsRepository,
        sleepTimeSeconds: float = 60,
        queueTimeoutSeconds: int = 3
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaRepository, TriviaRepository):
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 10 or sleepTimeSeconds > 300:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')

        self.__timber: Timber = timber
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds

        self.__superTriviaQuestionQueue: SimpleQueue[AbsTriviaQuestion] = SimpleQueue()
        self.__triviaQuestionQueue: SimpleQueue[AbsTriviaQuestion] = SimpleQueue()
        backgroundTaskHelper.createTask(self.__startSpooler())

    async def getSpooledTriviaQuestion(self, triviaFetchOptions: TriviaFetchOptions) -> Optional[AbsTriviaQuestion]:
        if not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaQuestion: Optional[AbsTriviaQuestion] = None

        if triviaFetchOptions.requireQuestionAnswerTriviaQuestion():
            if not self.__superTriviaQuestionQueue.empty():
                try:
                    triviaQuestion = self.__superTriviaQuestionQueue.get_nowait()
                except queue.Empty as e:
                    self.__timber.log('TriviaQuestionSpooler', f'Encountered queue.Empty when trying to retrieve a spooled super trivia question', e, traceback.format_exc())
        else:
            if not self.__triviaQuestionQueue.empty():
                try:
                    triviaQuestion = self.__triviaQuestionQueue.get_nowait()
                except queue.Empty as e:
                    self.__timber.log('TriviaQuestionSpooler', f'Encountered queue.Empty when trying to retrieve a spooled trivia question', e, traceback.format_exc())

        self.__timber.log('TriviaQuestionSpooler', f'Retrieved a spooled trivia question')
        return triviaQuestion

    async def __spoolNewSuperTriviaQuestion(self):
        # TODO
        self.__timber.log('TriviaQuestionSpooler', f'Finished spooling a super trivia question (qsize: {self.__superTriviaQuestionQueue.qsize()})')

    async def __spoolNewTriviaQuestion(self):
        # TODO 
        self.__timber.log('TriviaQuestionSpooler', f'Finished spooling a trivia question (qsize: {self.__triviaQuestionQueue.qsize()})')

    async def __startSpooler(self):
        while True:
            try:
                if self.__triviaQuestionQueue.qsize() < await self.__triviaSettingsRepository.getMaxTriviaQuestionSpoolSize():
                    await self.__spoolNewTriviaQuestion()

                if self.__triviaQuestionQueue.qsize() < await self.__triviaSettingsRepository.getMaxSuperTriviaQuestionSpoolSize():
                    await self.__spoolNewSuperTriviaQuestion()
            except Exception as e:
                self.__timber.log('TriviaQuestionSpooler', f'Encountered unknown Exception when refreshing spooler status', e, traceback.format_exc())

            await asyncio.sleep(self.__sleepTimeSeconds)
