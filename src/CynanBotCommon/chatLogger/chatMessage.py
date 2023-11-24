try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatLogger.absChatMessage import AbsChatMessage
    from CynanBotCommon.chatLogger.chatEventType import ChatEventType
except:
    import utils

    from chatLogger.absChatMessage import AbsChatMessage
    from chatLogger.chatEventType import ChatEventType


class ChatMessage(AbsChatMessage):

    def __init__(
        self,
        msg: str,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        super().__init__(
            chatEventType = ChatEventType.MESSAGE,
            twitchChannel = twitchChannel
        )

        if not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__msg: str = msg
        self.__userId: str = userId
        self.__userName: str = userName

    def getMsg(self) -> str:
        return self.__msg

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName
