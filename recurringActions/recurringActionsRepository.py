from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.recurringActionsJsonParserInterface import \
        RecurringActionsJsonParserInterface
    from CynanBotCommon.recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from recurringActions.recurringActionsJsonParserInterface import \
        RecurringActionsJsonParserInterface
    from recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from recurringActions.weatherRecurringAction import WeatherRecurringAction
    from recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface


class RecurringActionsRepository(RecurringActionsRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        recurringActionsJsonParser: RecurringActionsJsonParserInterface,
        timber: TimberInterface
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(recurringActionsJsonParser, RecurringActionsJsonParserInterface):
            raise ValueError(f'recurringActionsJsonParser argument is malformed: \"{recurringActionsJsonParser}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__recurringActionsJsonParser: RecurringActionsJsonParserInterface = recurringActionsJsonParser
        self.__timber: TimberInterface = timber

        self.__isDatabaseReady: bool = False

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def getWeatherRecurringAction(
        self,
        twitchChannel: str
    ) -> Optional[WeatherRecurringAction]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        # TODO

        return None

    async def getWordOfTheDayRecurringAction(
        self,
        twitchChannel: str
    ) -> Optional[WordOfTheDayRecurringAction]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        # TODO

        return None

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS recurringactions (
                        actiontype text NOT NULL,
                        configurationjson text DEFAULT NULL,
                        isenabled smallint DEFAULT 1 NOT NULL,
                        minutesbetween integer DEFAULT NULL,
                        twitchchannel public.citext NOT NULL,
                        PRIMARY KEY (actiontype, twitchchannel)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS recurringactions (
                        actiontype TEXT NOT NULL,
                        configurationjson TEXT DEFAULT NULL,
                        isenabled INTEGER DEFAULT 1 NOT NULL,
                        minutesbetween INTEGER DEFAULT NULL,
                        twitchchannel TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (actiontype, twitchchannel)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def setWeatherRecurringAction(
        self,
        action: WeatherRecurringAction
    ):
        if not isinstance(action, WeatherRecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        # TODO
        pass

    async def setWordOfTheDayRecurringAction(
        self,
        action: WordOfTheDayRecurringAction
    ):
        if not isinstance(action, WordOfTheDayRecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        # TODO
        pass
