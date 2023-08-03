from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
    from CynanBotCommon.weather.weatherReport import WeatherReport
except:
    import utils
    from recurringActions.recurringActionType import RecurringActionType
    from recurringActions.weatherRecurringAction import WeatherRecurringAction
    from weather.weatherReport import WeatherReport


class ImmutableWeatherRecurringAction(WeatherRecurringAction):

    def __init__(
        self,
        twitchChannel: str,
        alertsOnly: bool = False,
        enabled: bool = True,
        minutesBetween: Optional[int] = None,
        weatherReport: Optional[WeatherReport] = None
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(alertsOnly):
            raise ValueError(f'alertsOnly argument is malformed: \"{alertsOnly}\"')
        elif not utils.isValidBool(enabled):
            raise ValueError(f'enabled argument is malformed: \"{enabled}\"')
        elif minutesBetween is not None and not utils.isValidInt(minutesBetween):
            raise ValueError(f'minutesBetween argument is malformed: \"{minutesBetween}\"')
        elif minutesBetween is not None and (minutesBetween < 1 or minutesBetween >= utils.getIntMaxSafeSize()):
            raise ValueError(f'minutesBetween argument is out of bounds: {minutesBetween}')
        elif weatherReport is not None and not isinstance(weatherReport, WeatherReport):
            raise ValueError(f'weatherReport argument is malformed: \"{weatherReport}\"')

        self.__twitchChannel: str = twitchChannel
        self.__alertsOnly: bool = alertsOnly
        self.__enabled: bool = enabled
        self.__minutesBetween: Optional[int] = minutesBetween
        self.__weatherReport: Optional[WeatherReport] = weatherReport

    def getActionType(self) -> RecurringActionType:
        return RecurringActionType.WEATHER

    def getMinutesBetween(self) -> Optional[int]:
        return self.__minutesBetween

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def hasMinutesBetween(self) -> bool:
        return utils.isValidInt(self.__minutesBetween)

    def isAlertsOnly(self) -> bool:
        return self.__alertsOnly

    def isEnabled(self) -> bool:
        return self.__enabled

    def requireWeatherReport(self) -> WeatherReport:
        weatherReport = self.__weatherReport

        if weatherReport is None:
            raise RuntimeError(f'No weatherReport value has been set!')

        return weatherReport
