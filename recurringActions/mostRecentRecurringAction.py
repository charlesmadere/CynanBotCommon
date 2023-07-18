from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from recurringActions.recurringActionType import RecurringActionType
    from simpleDateTime import SimpleDateTime


class MostRecentRecurringAction():

    def __init__(
        self,
        actionType: Optional[RecurringActionType],
        dateTime: Optional[SimpleDateTime],
        twitchChannel: str
    ):
        if actionType is not None and not isinstance(actionType, RecurringActionType):
            raise ValueError(f'actionType argument is malformed: \"{actionType}\"')
        elif dateTime is not None and not isinstance(dateTime, SimpleDateTime):
            raise ValueError(f'dateTime argument is malformed: \"{dateTime}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__actionType: Optional[RecurringActionType] = actionType
        self.__dateTime: Optional[SimpleDateTime] = dateTime
        self.__twitchChannel: str = twitchChannel

    def getActionType(self) -> Optional[RecurringActionType]:
        return self.__actionType

    def getDateTime(self) -> Optional[SimpleDateTime]:
        return self.__dateTime

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def hasActionType(self) -> bool:
        return self.__actionType is not None

    def hasDateTime(self) -> bool:
        return self.__dateTime is not None
