try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime


class ChatMessage():

    def __init__(self, twitchChannel: str, userId: str, userName: str, msg: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')

        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName
        self.__msg: str = msg

        self.__sdt: SimpleDateTime = SimpleDateTime()

    def getMsg(self) -> str:
        return self.__msg

    def getSimpleDateTime(self) -> SimpleDateTime:
        return self.__sdt

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName
