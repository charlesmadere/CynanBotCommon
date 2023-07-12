try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.absRecurringActionConfiguration import \
        AbsRecurringActionConfiguration
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
except:
    import utils
    from recurringActions.absRecurringActionConfiguration import \
        AbsRecurringActionConfiguration
    from recurringActions.recurringActionType import RecurringActionType


class WeatherRecurringActionConfiguration(AbsRecurringActionConfiguration):

    def __init__(self, twitchChannel: str):
        super().__init__(
            actionType = RecurringActionType.WEATHER,
            twitchChannel = twitchChannel
        )

        self.__alertsOnly: bool = False

    def getAlertsOnly(self) -> bool:
        return self.__alertsOnly

    def setAlertsOnly(self, alertsOnly: bool):
        if not utils.isValidBool(alertsOnly):
            raise ValueError(f'alertsOnly argument is malformed: \"{alertsOnly}\"')

        self.__alertsOnly = alertsOnly
