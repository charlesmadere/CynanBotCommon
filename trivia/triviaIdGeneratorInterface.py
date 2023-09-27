from abc import ABC, abstractmethod
from typing import Optional


class TriviaIdGeneratorInterface(ABC):

    @abstractmethod
    async def generate(
        self,
        question: str,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> str:
        pass
