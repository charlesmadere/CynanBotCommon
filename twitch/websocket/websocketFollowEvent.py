try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime


class WebsocketFollowEvent():

    def __init__(
        self,
        followedAt: SimpleDateTime,
        broadcasterUserId: str,
        broadcasterUserLogin: str,
        broadcasterUserName: str,
        userId: str,
        userLogin: str,
        userName: str
    ):
        if not isinstance(followedAt, SimpleDateTime):
            raise ValueError(f'followedAt argument is malformed: \"{followedAt}\"')
        elif not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        elif not utils.isValidStr(broadcasterUserLogin):
            raise ValueError(f'broadcasterUserLogin argument is malformed: \"{broadcasterUserLogin}\"')
        elif not utils.isValidStr(broadcasterUserName):
            raise ValueError(f'broadcasterUserName argument is malformed: \"{broadcasterUserName}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userLogin):
            raise ValueError(f'userLogin argument is malformed: \"{userLogin}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__followedAt: SimpleDateTime = followedAt
        self.__broadcasterUserId: str = broadcasterUserId
        self.__broadcasterUserLogin: str = broadcasterUserLogin
        self.__broadcasterUserName: str = broadcasterUserName
        self.__userId: str = userId
        self.__userLogin: str = userLogin
        self.__userName: str = userName

    def getBroadcasterUserId(self) -> str:
        return self.__broadcasterUserId

    def getBroadcasterUserLogin(self) -> str:
        return self.__broadcasterUserLogin

    def getBroadcasterUserName(self) -> str:
        return self.__broadcasterUserName

    def getFollowedAt(self) -> SimpleDateTime:
        return self.__followedAt

    def getUserId(self) -> str:
        return self.__userId

    def getUserLogin(self) -> str:
        return self.__userLogin

    def getUserName(self) -> str:
        return self.__userName
