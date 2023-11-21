from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime


class SupStreamerChatter():

    def __init__(
        self,
        mostRecentSup: Optional[SimpleDateTime],
        userId: str
    ):
        if mostRecentSup is not None and not isinstance(mostRecentSup, SimpleDateTime):
            raise ValueError(f'mostRecentSup argument is malformed: \"{mostRecentSup}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        self.__mostRecentSup: Optional[SimpleDateTime] = mostRecentSup
        self.__userId: str = userId

    def getMostRecentSup(self) -> Optional[SimpleDateTime]:
        return self.__mostRecentSup

    def getUserId(self) -> str:
        return self.__userId
