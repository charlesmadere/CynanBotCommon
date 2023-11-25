from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
except:
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode


class TriviaContentScannerInterface(ABC):

    @abstractmethod
    async def verify(self, question: Optional[AbsTriviaQuestion]) -> TriviaContentCode:
        pass
