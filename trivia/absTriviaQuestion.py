from abc import ABC, abstractmethod
from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import \
        NoTriviaQuestionException
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils

    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import NoTriviaQuestionException
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class AbsTriviaQuestion(ABC):

    def __init__(
        self,
        category: Optional[str],
        categoryId: Optional[str],
        question: str,
        triviaId: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ):
        if not utils.isValidStr(question):
            raise NoTriviaQuestionException(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif triviaDifficulty is None:
            raise ValueError(f'triviaDifficulty argument is malformed: \"{triviaDifficulty}\"')
        elif triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')
        elif triviaType is None:
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        self.__category: Optional[str] = category
        self.__categoryId: Optional[str] = categoryId
        self.__question: str = question
        self.__triviaId: str = triviaId
        self.__triviaDifficulty: TriviaDifficulty = triviaDifficulty
        self.__triviaSource: TriviaSource = triviaSource
        self.__triviaType: TriviaType = triviaType

    def getCategory(self) -> Optional[str]:
        return self.__category

    def getCategoryId(self) -> Optional[str]:
        return self.__categoryId

    @abstractmethod
    def getCorrectAnswers(self) -> List[str]:
        pass

    @abstractmethod
    def getPrompt(self, delimiter: str = ' ') -> str:
        pass

    def getQuestion(self) -> str:
        return self.__question

    @abstractmethod
    def getResponses(self) -> List[str]:
        pass

    def getTriviaDifficulty(self) -> TriviaDifficulty:
        return self.__triviaDifficulty

    def getTriviaId(self) -> str:
        return self.__triviaId

    def getTriviaSource(self) -> TriviaSource:
        return self.__triviaSource

    def getTriviaType(self) -> TriviaType:
        return self.__triviaType

    def hasCategory(self) -> bool:
        return utils.isValidStr(self.__category)

    def hasCategoryId(self) -> bool:
        return utils.isValidStr(self.__categoryId)
