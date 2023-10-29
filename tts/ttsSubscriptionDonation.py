try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.tts.ttsDonation import TtsDonation
    from CynanBotCommon.tts.ttsDonationType import TtsDonationType
except:
    import utils
    from tts.ttsDonation import TtsDonation
    from tts.ttsDonationType import TtsDonationType


class TtsSubscriptionDonation(TtsDonation):

    def __init__(
        self,
        isAnonymous: bool,
        isGift: bool
    ):
        if not utils.isValidBool(isAnonymous):
            raise ValueError(f'isAnonymous argument is malformed: \"{isAnonymous}\"')
        elif not utils.isValidBool(isGift):
            raise ValueError(f'isGift argument is malformed: \"{isGift}\"')

        self.__isAnonymous: bool = isAnonymous
        self.__isGift: bool = isGift

    def getType(self) -> TtsDonationType:
        return TtsDonationType.SUBSCRIPTION

    def isAnonymous(self) -> bool:
        return self.__isAnonymous

    def isGift(self) -> bool:
        return self.__isGift
