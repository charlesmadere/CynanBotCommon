from abc import ABC, abstractmethod

try:
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
except:
    from trivia.absTriviaEvent import AbsTriviaEvent


class TriviaEventListener(ABC):

    @abstractmethod
    async def onNewTriviaEvent(self, event: AbsTriviaEvent):
        pass
