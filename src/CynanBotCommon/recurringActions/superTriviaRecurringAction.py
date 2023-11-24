from typing import Optional

try:
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
    from CynanBotCommon.recurringActions.recurringActionType import RecurringActionType
except:
    from recurringActions.recurringAction import RecurringAction
    from recurringActions.recurringActionType import RecurringActionType


class SuperTriviaRecurringAction(RecurringAction):

    def __init__(
        self,
        enabled: bool,
        twitchChannel: str,
        minutesBetween: Optional[int] = None
    ):
        super().__init__(
            enabled = enabled,
            twitchChannel = twitchChannel,
            minutesBetween = minutesBetween
        )

    def getActionType(self) -> RecurringActionType:
        return RecurringActionType.SUPER_TRIVIA
