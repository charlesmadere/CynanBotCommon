from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.tts.ttsDonation import TtsDonation
except:
    import utils
    from tts.ttsDonation import TtsDonation


class TtsEvent():

    def __init__(
        self,
        message: Optional[str],
        twitchChannel: str,
        userId: str,
        userName: str,
        donation: Optional[TtsDonation]
    ):
        if message is not None and not isinstance(message, str):
            raise ValueError(f'message argument is malformed: \"{message}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif donation is not None and not isinstance(donation, TtsDonation):
            raise ValueError(f'donation argument is malformed: \"{donation}\"')

        self.__message: Optional[str] = message
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName
        self.__donation: Optional[TtsDonation] = donation

    def getDonation(self) -> Optional[TtsDonation]:
        return self.__donation

    def getMessage(self) -> Optional[str]:
        return self.__message

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

    def __repr__(self) -> str:
        donationValue: Optional[Dict[str, Any]] = None

        if self.__donation is not None:
            donationValue = self.__donation.toDictionary()

        dictionary = {
            'donation': donationValue,
            'message': self.__message,
            'twitchChannel': self.__twitchChannel,
            'userId': self.__userId,
            'userName': self.__userName
        }

        return f'{dictionary}'
