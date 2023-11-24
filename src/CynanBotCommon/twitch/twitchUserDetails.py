try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.twitch.twitchBroadcasterType import \
        TwitchBroadcasterType
    from CynanBotCommon.twitch.twitchUserType import TwitchUserType
except:
    import utils

    from twitch.twitchBroadcasterType import TwitchBroadcasterType
    from twitch.twitchUserType import TwitchUserType


class TwitchUserDetails():

    def __init__(
        self,
        displayName: str,
        login: str,
        userId: str,
        broadcasterType: TwitchBroadcasterType,
        userType: TwitchUserType
    ):
        if not utils.isValidStr(displayName):
            raise ValueError(f'displayName argument is malformed: \"{displayName}\"')
        elif not utils.isValidStr(login):
            raise ValueError(f'login argument is malformed: \"{login}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not isinstance(broadcasterType, TwitchBroadcasterType):
            raise ValueError(f'broadcasterType argument is malformed: \"{broadcasterType}\"')
        elif not isinstance(userType, TwitchUserType):
            raise ValueError(f'userType argument is malformed: \"{userType}\"')

        self.__displayName: str = displayName
        self.__login: str = login
        self.__userId: str = userId
        self.__broadcasterType: TwitchBroadcasterType = broadcasterType
        self.__userType: TwitchUserType = userType

    def getBroadcasterType(self) -> TwitchBroadcasterType:
        return self.__broadcasterType

    def getDisplayName(self) -> str:
        return self.__displayName

    def getLogin(self) -> str:
        return self.__login

    def getUserId(self) -> str:
        return self.__userId

    def getUserType(self) -> TwitchUserType:
        return self.__userType
