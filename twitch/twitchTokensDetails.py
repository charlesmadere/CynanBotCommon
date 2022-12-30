try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchTokensDetails():

    def __init__(
        self,
        expiresInSeconds: int,
        accessToken: str,
        refreshToken: str
    ):
        if not utils.isValidInt(expiresInSeconds):
            raise ValueError(f'expiresInSeconds argument is malformed: \"{expiresInSeconds}\"')
        elif not utils.isValidStr(accessToken):
            raise ValueError(f'accessToken argument is malformed: \"{accessToken}\"')
        elif not utils.isValidStr(refreshToken):
            raise ValueError(f'refreshToken argument is malformed: \"{refreshToken}\"')

        self.__expiresInSeconds: int = expiresInSeconds
        self.__accessToken: str = accessToken
        self.__refreshToken: str = refreshToken

    def getAccessToken(self) -> str:
        return self.__accessToken

    def getExpiresInSeconds(self) -> int:
        return self.__expiresInSeconds

    def getRefreshToken(self) -> str:
        return self.__refreshToken
