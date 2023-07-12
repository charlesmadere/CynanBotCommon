from abc import ABC

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
except:
    import utils
    from recurringActions.recurringActionType import RecurringActionType


class AbsRecurringAction(ABC):

    def __init__(
        self,
        actionType: RecurringActionType,
        twitchChannel: str
    ):
        if not isinstance(actionType, RecurringActionType):
            raise ValueError(f'actionType argument is malformed: \"{actionType}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__actionType: RecurringActionType = actionType
        self.__twitchChannel: str = twitchChannel

    def getActionType(self) -> RecurringActionType:
        return self.__actionType

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel
