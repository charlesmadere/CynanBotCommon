try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketSubscriptionCondition():

    def __init__(
        self,
        broadcasterUserId: str
    ):
        if not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')

        self.__broadcasterUserId: str = broadcasterUserId

    def getBroadcasterUserId(self) -> str:
        return self.__broadcasterUserId
