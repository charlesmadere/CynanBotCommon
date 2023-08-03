from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.recurringActions.superTriviaRecurringAction import \
        SuperTriviaRecurringAction
except:
    import utils
    from recurringActions.recurringActionType import RecurringActionType
    from recurringActions.superTriviaRecurringAction import \
        SuperTriviaRecurringAction


class ImmutableSuperTriviaRecurringAction(SuperTriviaRecurringAction):

    def __init__(
        self,
        twitchChannel: str,
        enabled: bool = True,
        minutesBetween: Optional[int] = None
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(enabled):
            raise ValueError(f'enabled argument is malformed: \"{enabled}\"')
        elif minutesBetween is not None and not utils.isValidInt(minutesBetween):
            raise ValueError(f'minutesBetween argument is malformed: \"{minutesBetween}\"')
        elif minutesBetween is not None and (minutesBetween < 1 or minutesBetween >= utils.getIntMaxSafeSize()):
            raise ValueError(f'minutesBetween argument is out of bounds: {minutesBetween}')

        self.__twitchChannel: str = twitchChannel
        self.__enabled: bool = enabled
        self.__minutesBetween: Optional[int] = minutesBetween

    def getActionType(self) -> RecurringActionType:
        return RecurringActionType.SUPER_TRIVIA

    def getMinutesBetween(self) -> Optional[int]:
        return self.__minutesBetween

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def hasMinutesBetween(self) -> bool:
        return utils.isValidInt(self.__minutesBetween)

    def isEnabled(self) -> bool:
        return self.__enabled
