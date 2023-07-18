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
        actionType: RecurringActionType,
        dateTime: SimpleDateTime,
        twitchChannel: str
    ):
        if not isinstance(actionType, RecurringActionType):
            raise ValueError(f'actionType argument is malformed: \"{actionType}\"')
        elif not isinstance(dateTime, SimpleDateTime):
            raise ValueError(f'dateTime argument is malformed: \"{dateTime}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__actionType: RecurringActionType = actionType
        self.__dateTime: SimpleDateTime = dateTime
        self.__twitchChannel: str = twitchChannel

    def getActionType(self) -> RecurringActionType:
        return self.__actionType

    def getDateTime(self) -> SimpleDateTime:
        return self.__dateTime

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def hasActionType(self) -> bool:
        return self.__actionType is not None

    def hasDateTime(self) -> bool:
        return self.__dateTime is not None
