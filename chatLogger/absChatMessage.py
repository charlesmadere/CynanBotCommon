from abc import ABC

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatLogger.chatEventType import ChatEventType
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime

    from chatLogger.chatEventType import ChatEventType


class AbsChatMessage(ABC):

    def __init__(
        self,
        chatEventType: ChatEventType,
        twitchChannel: str
    ):
        if chatEventType is None:
            raise ValueError(f'chatEventType argument is malformed: \"{chatEventType}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__chatEventType: ChatEventType = chatEventType
        self.__twitchChannel: str = twitchChannel
        self.__sdt: SimpleDateTime = SimpleDateTime()

    def getChatEventType(self) -> ChatEventType:
        return self.__chatEventType

    def getSimpleDateTime(self) -> SimpleDateTime:
        return self.__sdt

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel
