from typing import Optional

try:
    from CynanBotCommon.recurringActions.recurringActionListener import \
        RecurringActionListener
    from CynanBotCommon.recurringActions.recurringActionsHelperInterface import \
        RecurringActionsHelperInterface
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
except:
    from recurringActions.recurringActionListener import \
        RecurringActionListener
    from recurringActions.recurringActionsHelperInterface import \
        RecurringActionsHelperInterface
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType


class RecurringActionsHelper(RecurringActionsHelperInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase

        self.__isDatabaseReady: bool = False
        self.__actionListener: Optional[RecurringActionListener] = None

    def setRecurringActionListener(self, listener: Optional[RecurringActionListener]):
        if listener is not None and not isinstance(listener, RecurringActionListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__actionListener = listener

    def startRecurringActions(self):
        # TODO
        pass
