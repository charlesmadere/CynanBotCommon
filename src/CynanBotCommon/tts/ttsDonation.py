from abc import ABC, abstractmethod
from typing import Any, Dict

try:
    from CynanBotCommon.tts.ttsDonationType import TtsDonationType
except:
    from tts.ttsDonationType import TtsDonationType


class TtsDonation(ABC):

    @abstractmethod
    def getType(self) -> TtsDonationType:
        pass

    @abstractmethod
    def toDictionary(self) -> Dict[str, Any]:
        pass
