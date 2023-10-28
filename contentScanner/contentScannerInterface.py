from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.contentScanner.contentCode import ContentCode
except:
    from contentScanner.contentCode import ContentCode


class ContentScannerInterface(ABC):

    @abstractmethod
    async def scan(self, message: Optional[str]) -> ContentCode:
        pass
