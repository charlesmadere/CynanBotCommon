from abc import ABC, abstractmethod

try:
    from CynanBotCommon.tts.ttsDonationType import TtsDonationType
except:
    from tts.ttsDonationType import TtsDonationType


class TtsDonation(ABC):

    @abstractmethod
    def getType(self) -> TtsDonationType:
        pass
