from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.trivia.bannedTriviaQuestion import BannedTriviaQuestion
    from CynanBotCommon.trivia.banTriviaQuestionResult import \
        BanTriviaQuestionResult
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    from trivia.bannedTriviaQuestion import BannedTriviaQuestion
    from trivia.banTriviaQuestionResult import BanTriviaQuestionResult
    from trivia.triviaSource import TriviaSource


class BannedTriviaIdsRepositoryInterface(ABC):

    @abstractmethod
    async def ban(
        self,
        triviaId: str,
        userId: str,
        triviaSource: TriviaSource
    ) -> BanTriviaQuestionResult:
        pass

    @abstractmethod
    async def getInfo(
        self,
        triviaId: str,
        triviaSource: TriviaSource
    ) -> Optional[BannedTriviaQuestion]:
        pass

    @abstractmethod
    async def isBanned(self, triviaId: str, triviaSource: TriviaSource) -> bool:
        pass

    @abstractmethod
    async def unban(
        self,
        triviaId: str,
        triviaSource: TriviaSource
    ) -> BanTriviaQuestionResult:
        pass
