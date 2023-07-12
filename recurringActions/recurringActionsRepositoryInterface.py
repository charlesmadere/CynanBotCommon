from abc import ABC, abstractmethod

try:
    from CynanBotCommon.recurringActions.weatherRecurringActionConfiguration import \
        WeatherRecurringActionConfiguration
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringActionConfiguration import \
        WordOfTheDayRecurringActionConfiguration
except:
    from recurringActions.weatherRecurringActionConfiguration import \
        WeatherRecurringActionConfiguration
    from recurringActions.wordOfTheDayRecurringActionConfiguration import \
        WordOfTheDayRecurringActionConfiguration


class RecurringActionsRepositoryInterface(ABC):

    @abstractmethod
    async def configureWeatherRecurringAction(
        self,
        action: WeatherRecurringActionConfiguration
    ):
        pass

    @abstractmethod
    async def configureWordOfTheDayRecurringAction(
        self,
        action: WordOfTheDayRecurringActionConfiguration
    ):
        pass
