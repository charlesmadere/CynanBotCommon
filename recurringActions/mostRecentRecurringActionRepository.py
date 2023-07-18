from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.mostRecentRecurringAction import \
        MostRecentRecurringAction
    from CynanBotCommon.recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from recurringActions.mostRecentRecurringAction import \
        MostRecentRecurringAction
    from recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from recurringActions.recurringAction import RecurringAction
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface


class MostRecentRecurringActionRepository(MostRecentRecurringActionRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backingDatabase: BackingDatabase = BackingDatabase
        self.__timber: TimberInterface = timber

        self.__isDatabaseReady: bool = False

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS mostrecentrecurringaction (
                        actiontype text NOT NULL,
                        datetime text NOT NULL,
                        twitchchannel public.citext NOT NULL PRIMARY KEY
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS mostrecentrecurringaction (
                        actiontype TEXT NOT NULL,
                        datetime TEXT NOT NULL,
                        twitchchannel TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def getMostRecentRecurringAction(
        self,
        twitchChannel: str
    ) -> Optional[MostRecentRecurringAction]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        # TODO
        pass

    async def setMostRecentRecurringAction(self, action: RecurringAction):
        if not isinstance(action, RecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        # TODO
        pass
