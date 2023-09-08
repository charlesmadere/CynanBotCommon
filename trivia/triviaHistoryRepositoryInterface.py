from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaQuestionReference import \
        TriviaQuestionReference
except:
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaQuestionReference import TriviaQuestionReference


class TriviaHistoryRepositoryInterface(ABC):

    @abstractmethod
    async def getMostRecentTriviaQuestionDetails(
        self,
        emote: str,
        twitchChannel: str
    ) -> Optional[TriviaQuestionReference]:
        pass

    @abstractmethod
    async def verify(
        self,
        question: AbsTriviaQuestion,
        emote: str,
        twitchChannel: str
    ) -> TriviaContentCode:
        pass
