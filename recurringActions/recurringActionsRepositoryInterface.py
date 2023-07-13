from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
except:
    from recurringActions.weatherRecurringAction import WeatherRecurringAction
    from recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction


class RecurringActionsRepositoryInterface(ABC):

    @abstractmethod
    async def getWeatherRecurringAction(
        self,
        twitchChannel: str
    ) -> Optional[WeatherRecurringAction]:
        pass

    @abstractmethod
    async def getWordOfTheDayRecurringAction(
        self,
        twitchChannel: str
    ) -> Optional[WordOfTheDayRecurringAction]:
        pass

    @abstractmethod
    async def setWeatherRecurringAction(
        self,
        action: WeatherRecurringAction
    ):
        pass

    @abstractmethod
    async def setWordOfTheDayRecurringAction(
        self,
        action: WordOfTheDayRecurringAction
    ):
        pass
