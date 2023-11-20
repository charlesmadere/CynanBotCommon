from typing import Any, Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime


class CheerActionRemodData():

    def __init__(
        self,
        remodDateTime: SimpleDateTime,
        broadcasterUserId: str,
        userId: str
    ):
        if not isinstance(remodDateTime, SimpleDateTime):
            raise ValueError(f'remodDateTime argument is malformed: \"{remodDateTime}\"')
        elif not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        self.__remodDateTime: SimpleDateTime = remodDateTime
        self.__broadcasterUserId: str = broadcasterUserId
        self.__userId: str = userId

    def getBroadcasterUserId(self) -> str:
        return self.__broadcasterUserId

    def getRemodDateTime(self) -> SimpleDateTime:
        return self.__remodDateTime

    def getUserId(self) -> str:
        return self.__userId

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'broadcasterUserId': self.__broadcasterUserId,
            'remodDateTime': self.__remodDateTime,
            'userId': self.__userId
        }
