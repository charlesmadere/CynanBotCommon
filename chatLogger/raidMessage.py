import locale

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatLogger.absChatMessage import AbsChatMessage
    from CynanBotCommon.chatLogger.chatEventType import ChatEventType
except:
    import utils

    from chatLogger.absChatMessage import AbsChatMessage
    from chatLogger.chatEventType import ChatEventType


class RaidMessage(AbsChatMessage):

    def __init__(
        self,
        raidSize: int,
        fromWho: str,
        twitchChannel: str
    ):
        super().__init__(
            chatEventType = ChatEventType.RAID,
            twitchChannel = twitchChannel
        )

        if not utils.isValidNum(raidSize):
            raise ValueError(f'raidSize argument is malformed: \"{raidSize}\"')
        elif raidSize < 0:
            raise ValueError(f'raidSize argument is out of bounds: {raidSize}')
        elif not utils.isValidStr(fromWho):
            raise ValueError(f'fromWho argument is malformed: \"{fromWho}\"')

        self.__raidSize: int = raidSize
        self.__fromWho: str = fromWho

    def getFromWho(self) -> str:
        return self.__fromWho

    def getRaidSize(self) -> int:
        return self.__raidSize

    def getRaidSizeStr(self) -> str:
        return locale.format_string("%d", self.__raidSize, grouping = True)
