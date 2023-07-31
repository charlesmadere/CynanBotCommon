from abc import abstractmethod

try:
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
    from CynanBotCommon.weather.weatherReport import WeatherReport
except:
    from recurringActions.recurringAction import RecurringAction
    from weather.weatherReport import WeatherReport


class WeatherRecurringAction(RecurringAction):

    @abstractmethod
    def isAlertsOnly(self) -> bool:
        pass

    @abstractmethod
    def requireWeatherReport(self) -> WeatherReport:
        pass
