from typing import Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.supStreamer.supStreamerChatter import \
        SupStreamerChatter
except:
    import utils
    from supStreamer.supStreamerChatter import SupStreamerChatter


class SupStreamerAction():

    def __init__(
        self,
        chatters: Set[SupStreamerChatter],
        broadcasterUserId: str,
        broadcasterUserName: str
    ):
        if not isinstance(chatters, Set) or not utils.hasItems(chatters):
            raise ValueError(f'chatters argument is malformed: \"{chatters}\"')
        elif not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        elif not utils.isValidStr(broadcasterUserName):
            raise ValueError(f'broadcasterUserName argument is malformed: \"{broadcasterUserName}\"')

        self.__chatters: Set[SupStreamerChatter] = chatters
        self.__broadcasterUserId: str = broadcasterUserId
        self.__broadcasterUserName: str = broadcasterUserName

    def getBroadcasterUserId(self) -> str:
        return self.__broadcasterUserId

    def getBroadcasterUserName(self) -> str:
        return self.__broadcasterUserName

    def getChatters(self) -> Set[SupStreamerChatter]:
        return self.__chatters
