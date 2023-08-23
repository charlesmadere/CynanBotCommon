from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.trivia.additionalTriviaAnswers import \
        AdditionalTriviaAnswers
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    from trivia.additionalTriviaAnswers import AdditionalTriviaAnswers
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class AdditionalTriviaAnswersRepositoryInterface(ABC):

    @abstractmethod
    async def addAdditionalTriviaAnswer(
        self,
        additionalAnswer: str,
        triviaId: str,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ) -> AdditionalTriviaAnswers:
        pass

    @abstractmethod
    async def deleteAdditionalTriviaAnswers(
        self,
        triviaId: str,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ) -> Optional[AdditionalTriviaAnswers]:
        pass

    @abstractmethod
    async def getAdditionalTriviaAnswers(
        self,
        triviaId: str,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ) -> Optional[AdditionalTriviaAnswers]:
        pass
