from abc import ABC, abstractmethod

try:
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    from trivia.triviaSource import TriviaSource


class BannedTriviaIdsRepositoryInterface(ABC):

    @abstractmethod
    async def ban(self, triviaId: str, userId: str, triviaSource: TriviaSource):
        pass

    @abstractmethod
    async def isBanned(self, triviaId: str, triviaSource: TriviaSource) -> bool:
        pass

    @abstractmethod
    async def unban(self, triviaId: str, triviaSource: TriviaSource):
        pass
