from abc import ABC, abstractmethod
from typing import Optional


class ContentScannerInterface(ABC):

    @abstractmethod
    async def scan(self, message: Optional[str]):
        pass
