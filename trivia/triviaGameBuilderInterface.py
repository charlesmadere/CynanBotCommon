from abc import ABC, abstractmethod

try:
    from CynanBotCommon.trivia.newSuperTriviaGameEvent import \
        NewSuperTriviaGameEvent
    from CynanBotCommon.trivia.newTriviaGameEvent import NewTriviaGameEvent
except:
    from trivia.newSuperTriviaGameEvent import NewSuperTriviaGameEvent
    from trivia.newTriviaGameEvent import NewTriviaGameEvent    


class TriviaGameBuilderInterface(ABC):

    @abstractmethod
    async def createNewTriviaGame(self, twitchChannel: str) -> NewTriviaGameEvent:
        pass

    @abstractmethod
    async def createNewSuperTriviaGame(self, twitchChannel: str) -> NewSuperTriviaGameEvent:
        pass
