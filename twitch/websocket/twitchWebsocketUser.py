from typing import Any

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchWebsocketUser():

    def __init__(
        self,
        twitchAccessToken: str,
        userId: str,
        userName: str
    ):
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__twitchAccessToken: str = twitchAccessToken
        self.__userId: str = userId
        self.__userName: str = userName

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TwitchWebsocketUser):
            return False

        return self.__userId == other.__userId

    def getTwitchAccessToken(self) -> str:
        return self.__twitchAccessToken

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

    def __hash__(self) -> int:
        return hash(self.__userId)

    def __repr__(self) -> str:
        return self.getUserName()
