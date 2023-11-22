from typing import Any, Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.twitch.twitchSubscriberTier import TwitchSubscriberTier
except:
    import utils

    from twitch.twitchSubscriberTier import TwitchSubscriberTier


class WebsocketSubGift():

    def __init__(
        self,
        recipientUserId: str,
        recipientUserLogin: str,
        recipientUserName: str,
        subTier: TwitchSubscriberTier
    ):
        if not utils.isValidStr(recipientUserId):
            raise ValueError(f'recipientUserId argument is malformed: \"{recipientUserId}\"')
        if not utils.isValidStr(recipientUserLogin):
            raise ValueError(f'recipientUserLogin argument is malformed: \"{recipientUserLogin}\"')
        if not utils.isValidStr(recipientUserName):
            raise ValueError(f'recipientUserName argument is malformed: \"{recipientUserName}\"')
        elif not isinstance(subTier, TwitchSubscriberTier):
            raise ValueError(f'subTier argument is malformed: \"{subTier}\"')

        self.__recipientUserId: str = recipientUserId
        self.__recipientUserLogin: str = recipientUserLogin
        self.__recipientUserName: str = recipientUserName
        self.__subTier: TwitchSubscriberTier = subTier

    def getRecipientUserId(self) -> str:
        return self.__recipientUserId

    def getRecipientUserLogin(self) -> str:
        return self.__recipientUserLogin

    def getRecipientUserName(self) -> str:
        return self.__recipientUserName

    def getSubTier(self) -> TwitchSubscriberTier:
        return self.__subTier

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'recipientUserId': self.__recipientUserId,
            'recipientUserLogin': self.__recipientUserLogin,
            'recipientUserName': self.__recipientUserName,
            'subTier': self.__subTier
        }
