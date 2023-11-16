import locale
from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cheerActions.cheerActionRequirement import \
        CheerActionRequirement
    from CynanBotCommon.cheerActions.cheerActionType import CheerActionType
except:
    import utils
    from cheerActions.cheerActionRequirement import CheerActionRequirement
    from cheerActions.cheerActionType import CheerActionType


class CheerAction():

    def __init__(
        self,
        actionRequirement: CheerActionRequirement,
        actionType: CheerActionType,
        amount: int,
        durationSeconds: Optional[int],
        userId: str,
        userName: str
    ):
        if not isinstance(actionRequirement, CheerActionRequirement):
            raise ValueError(f'actionRequirement argument is malformed: \"{actionRequirement}\"')
        elif not isinstance(actionType, CheerActionType):
            raise ValueError(f'actionType argument is malformed: \"{actionType}\"')
        elif not utils.isValidInt(amount):
            raise ValueError(f'amount argument is malformed: \"{amount}\"')
        elif amount < 1 or amount > utils.getIntMaxSafeSize():
            raise ValueError(f'amount argument is out of bounds: {amount}')
        elif durationSeconds is not None and not utils.isValidInt(durationSeconds):
            raise ValueError(f'durationSeconds argument is malformed: \"{durationSeconds}\"')
        elif durationSeconds is not None and (durationSeconds < 1 or durationSeconds > 1209600):
            raise ValueError(f'durationSeconds argument is out of bounds: {durationSeconds}')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__actionRequirement: CheerActionRequirement = actionRequirement
        self.__actionType: CheerActionType = actionType
        self.__amount: int = amount
        self.__durationSeconds: Optional[int] = durationSeconds
        self.__userId: str = userId
        self.__userName: str = userName

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CheerAction):
            return False

        return self.__actionRequirement is other.__actionRequirement and \
            self.__actionType is other.__actionType and \
            self.__amount == other.__amount and \
            self.__durationSeconds == other.__durationSeconds and \
            self.__userId == other.__userId

    def getActionRequirement(self) -> CheerActionRequirement:
        return self.__actionRequirement

    def getActionType(self) -> CheerActionType:
        return self.__actionType

    def getAmount(self) -> int:
        return self.__amount

    def getAmountStr(self) -> str:
        return locale.format_string("%d", self.__amount, grouping = True)

    def getDurationSeconds(self) -> Optional[int]:
        return self.__durationSeconds

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

    def __hash__(self) -> int:
        return hash((self.__actionRequirement, self.__actionType, self.__amount, self.__durationSeconds, self.__userId))

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'actionRequirement': self.__actionRequirement,
            'actionType': self.__actionType,
            'amount': self.__amount,
            'durationSeconds': self.__durationSeconds,
            'userId': self.__userId,
            'userName': self.__userName
        }
