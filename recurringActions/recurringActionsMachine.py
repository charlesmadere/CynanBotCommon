from queue import SimpleQueue
from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.recurringActions.absRecurringAction import \
        AbsRecurringAction
    from CynanBotCommon.recurringActions.recurringActionListener import \
        RecurringActionListener
    from CynanBotCommon.recurringActions.recurringActionsMachineInterface import \
        RecurringActionsMachineInterface
    from CynanBotCommon.recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from recurringActions.absRecurringAction import AbsRecurringAction
    from recurringActions.recurringActionListener import \
        RecurringActionListener
    from recurringActions.recurringActionsMachineInterface import \
        RecurringActionsMachineInterface
    from recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from timber.timberInterface import TimberInterface


class RecurringActionsMachine(RecurringActionsMachineInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        recurringActionsRepositoryInterface: RecurringActionsRepositoryInterface,
        timber: TimberInterface,
        sleepTimeSeconds: float = 30,
        queueTimeoutSeconds: int = 3
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(recurringActionsRepositoryInterface, RecurringActionsRepositoryInterface):
            raise ValueError(f'recurringActionsRepositoryInterface argument is malformed: \"{recurringActionsRepositoryInterface}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 15 or sleepTimeSeconds > 300:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__recurringActionsRepositoryInterface: RecurringActionsRepositoryInterface = recurringActionsRepositoryInterface
        self.__timber: TimberInterface = timber
        self.__sleepTimeoutSeconds: float = sleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds

        self.__isStarted: bool = False
        self.__actionListener: Optional[RecurringActionListener] = None
        self.__actionQueue: SimpleQueue[AbsRecurringAction] = SimpleQueue()

    def setRecurringActionListener(self, listener: Optional[RecurringActionListener]):
        if listener is not None and not isinstance(listener, RecurringActionListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__actionListener = listener

    def startRecurringActions(self):
        if self.__isStarted:
            self.__timber.log('RecurringActionsMachine', 'Not starting RecurringActionsMachine as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('RecurringActionsMachine', 'Starting RecurringActionsMachine...')

        self.__backgroundTaskHelper.createTask(self.__startRefreshLoop())

    async def __startRefreshLoop(self):
        # TODO
        pass
