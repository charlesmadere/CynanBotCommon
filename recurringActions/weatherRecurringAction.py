from abc import abstractmethod

try:
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
except:
    from recurringActions.recurringAction import RecurringAction


class WeatherRecurringAction(RecurringAction):

    @abstractmethod
    def isAlertsOnly(self) -> bool:
        pass
