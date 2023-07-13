from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.mutableRecurringAction import \
        MutableRecurringAction
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
except:
    import utils
    from recurringActions.mutableRecurringAction import MutableRecurringAction
    from recurringActions.recurringActionType import RecurringActionType
    from recurringActions.weatherRecurringAction import WeatherRecurringAction


class MutableWeatherRecurringAction(WeatherRecurringAction, MutableRecurringAction):

    def __init__(
        self,
        twitchChannel: str,
        alertsOnly: bool = False,
        enabled: bool = True,
        minutesBetween: Optional[int] = None
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(alertsOnly):
            raise ValueError(f'alertsOnly argument is malformed: \"{alertsOnly}\"')
        elif not utils.isValidBool(enabled):
            raise ValueError(f'enabled argument is malformed: \"{enabled}\"')
        if not utils.isValidInt(minutesBetween):
            raise ValueError(f'minutesBetween argument is malformed: \"{minutesBetween}\"')
        elif minutesBetween < 1 or minutesBetween >= utils.getIntMaxSafeSize():
            raise ValueError(f'minutesBetween argument is out of bounds: {minutesBetween}')

        self.__twitchChannel: str = twitchChannel
        self.__alertsOnly: bool = alertsOnly
        self.__enabled: bool = enabled
        self.__minutesBetween: Optional[int] = minutesBetween

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

    def setAlertsOnly(self, alertsOnly: bool):
        if not utils.isValidBool(alertsOnly):
            raise ValueError(f'alertsOnly argument is malformed: \"{alertsOnly}\"')

        self.__alertsOnly = alertsOnly

    def setEnabled(self, enabled: bool):
        if not utils.isValidBool(enabled):
            raise ValueError(f'enabled argument is malformed: \"{enabled}\"')

        self.__enabled = enabled

    def setMinutesBetween(self, minutesBetween: Optional[int]):
        if not utils.isValidInt(minutesBetween):
            raise ValueError(f'minutesBetween argument is malformed: \"{minutesBetween}\"')
        elif minutesBetween < 1 or minutesBetween >= utils.getIntMaxSafeSize():
            raise ValueError(f'minutesBetween argument is out of bounds: {minutesBetween}')

        self.__minutesBetween = minutesBetween
