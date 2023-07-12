try:
    from CynanBotCommon.recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from CynanBotCommon.recurringActions.weatherRecurringActionConfiguration import \
        WeatherRecurringActionConfiguration
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringActionConfiguration import \
        WordOfTheDayRecurringActionConfiguration
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    from recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from recurringActions.weatherRecurringActionConfiguration import \
        WeatherRecurringActionConfiguration
    from recurringActions.wordOfTheDayRecurringActionConfiguration import \
        WordOfTheDayRecurringActionConfiguration
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface


class RecurringActionsRepository(RecurringActionsRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber

        self.__isDatabaseReady: bool = False

    async def configureWeatherRecurringAction(
        self,
        action: WeatherRecurringActionConfiguration
    ):
        if not isinstance(action, WeatherRecurringActionConfiguration):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        # TODO
        pass

    async def configureWordOfTheDayRecurringAction(
        self,
        action: WordOfTheDayRecurringActionConfiguration
    ):
        if not isinstance(action, WordOfTheDayRecurringActionConfiguration):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        # TODO
        pass
