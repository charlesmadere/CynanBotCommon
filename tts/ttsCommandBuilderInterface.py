from abc import ABC, abstractmethod
from typing import Optional


class TtsCommandBuilderInterface(ABC):

    @abstractmethod
    async def buildAndCleanCommand(self, command: Optional[str]) -> Optional[str]:
        pass
