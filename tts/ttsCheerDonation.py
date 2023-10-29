try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.tts.ttsDonation import TtsDonation
    from CynanBotCommon.tts.ttsDonationType import TtsDonationType
except:
    import utils
    from tts.ttsDonation import TtsDonation
    from tts.ttsDonationType import TtsDonationType


class TtsCheerDonation(TtsDonation):

    def __init__(self, bits: int):
        if not utils.isValidInt(bits):
            raise ValueError(f'bits argument is malformed: \"{bits}\"')
        elif bits < 1 or bits > utils.getIntMaxSafeSize():
            raise ValueError(f'bits argument is out of bounds: {bits}')

        self.__bits: int = bits

    def getBits(self) -> int:
        return self.__bits

    def getType(self) -> TtsDonationType:
        return TtsDonationType.CHEER
