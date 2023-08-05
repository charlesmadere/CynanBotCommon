from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
except:
    import utils
    from recurringActions.recurringAction import RecurringAction
    from recurringActions.recurringActionType import RecurringActionType


class WeatherRecurringAction(RecurringAction):

    def __init__(
        self,
        enabled: bool,
        twitchChannel: str,
        alertsOnly: bool = False,
        minutesBetween: Optional[int] = None
    ):
        super().__init__(
            enabled = enabled,
            twitchChannel = twitchChannel,
            minutesBetween = minutesBetween
        )

        if not utils.isValidBool(alertsOnly):
            raise ValueError(f'alertsOnly argument is malformed: \"{alertsOnly}\"')

        self.__alertsOnly: bool = alertsOnly

    def getActionType(self) -> RecurringActionType:
        return RecurringActionType.WEATHER

    def isAlertsOnly(self) -> bool:
        return self.__alertsOnly
