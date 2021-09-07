from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaDifficulty(Enum):

    EASY = auto()
    HARD = auto()
    MEDIUM = auto()
    UNKNOWN = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            return TriviaDifficulty.UNKNOWN

        text = text.lower()

        if text == 'easy':
            return TriviaDifficulty.EASY
        elif text == 'hard':
            return TriviaDifficulty.HARD
        elif text == 'medium':
            return TriviaDifficulty.MEDIUM
        else:
            return TriviaDifficulty.UNKNOWN


class TriviaSource(Enum):

    J_SERVICE = auto()
    LOCAL_TRIVIA_REPOSITORY = auto()
    OPEN_TRIVIA_DATABASE = auto()
    WILL_FRY_TRIVIA_API = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'j_service':
            return TriviaSource.J_SERVICE
        elif text == 'local_trivia':
            return TriviaSource.LOCAL_TRIVIA_REPOSITORY
        elif text == 'open_trivia':
            return TriviaSource.OPEN_TRIVIA_DATABASE
        elif text == 'will_fry_trivia':
            return TriviaSource.WILL_FRY_TRIVIA_API
        else:
            raise ValueError(f'unknown TriviaSource: \"{text}\"')


class TriviaType(Enum):

    MULTIPLE_CHOICE = auto()
    QUESTION_ANSWER = auto()
    TRUE_FALSE = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'boolean':
            return TriviaType.TRUE_FALSE
        elif text == 'multiple' or text == 'multiple choice':
            return TriviaType.MULTIPLE_CHOICE
        else:
            raise ValueError(f'unknown TriviaType: \"{text}\"')


class AbsTriviaQuestion(ABC):

    def __init__(
        self,
        category: str,
        question: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ):
        if not utils.isValidStr(question):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif triviaDifficulty is None:
            raise ValueError(f'triviaDifficulty argument is malformed: \"{triviaDifficulty}\"')
        elif triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')
        elif triviaType is None:
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        self.__category: str = category
        self.__question: str = question
        self.__triviaDifficulty: TriviaDifficulty = triviaDifficulty
        self.__triviaSource: TriviaSource = triviaSource
        self.__triviaType: TriviaType = triviaType

    def getAnswerReveal(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        correctAnswers = self.getCorrectAnswers()
        return delimiter.join(correctAnswers)

    def getCategory(self) -> str:
        return self.__category

    @abstractmethod
    def getCorrectAnswers(self) -> List[str]:
        pass

    @abstractmethod
    def getPrompt(self, delimiter: str = ', ') -> str:
        pass

    def getQuestion(self) -> str:
        return self.__question

    @abstractmethod
    def getResponses(self) -> List[str]:
        pass

    def getTriviaDifficulty(self) -> TriviaDifficulty:
        return self.__triviaDifficulty

    def getTriviaSource(self) -> TriviaSource:
        return self.__triviaSource

    def getTriviaType(self) -> TriviaType:
        return self.__triviaType

    def hasCategory(self) -> bool:
        return utils.isValidStr(self.__category)


class MultipleChoiceTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[str],
        multipleChoiceResponses: List[str],
        category: str,
        question: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource
    ):
        super().__init__(
            category = category,
            question = question,
            triviaDifficulty = triviaDifficulty,
            triviaSource = triviaSource,
            triviaType = TriviaType.MULTIPLE_CHOICE,
        )

        if not utils.areValidStrs(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')
        elif not utils.hasItems(multipleChoiceResponses):
            raise ValueError(f'multipleChoiceResponses argument is malformed: \"{multipleChoiceResponses}\"')

        self.__correctAnswers: List[str] = correctAnswers
        self.__multipleChoiceResponses: List[str] = multipleChoiceResponses

    def getAnswerReveal(self, delimiter: str = ' ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        return delimiter.join(self.getCorrectAnswers())

    def getCorrectAnswers(self) -> List[str]:
        answerStrings: List[str] = list()
        index = 0

        for correctAnswerChar in self.getCorrectAnswerChars():
            answerStrings.append(f'[{correctAnswerChar}] {self.__correctAnswers[index]}')
            index = index + 1

        return answerStrings

    def getCorrectAnswerChars(self) -> List[str]:
        answerOrdinals = self.getCorrectAnswerOrdinals()
        correctAnswerChars: List[str] = list()

        for answerOrdinal in answerOrdinals:
            correctAnswerChars.append(chr(ord('A') + answerOrdinal))

        if not utils.hasItems(correctAnswerChars):
            raise RuntimeError(f'Couldn\'t find any correct answer chars within \"{self.__correctAnswers}\"')
        elif len(correctAnswerChars) != len(self.__correctAnswers):
            raise RuntimeError(f'The length of correctAnswerChars \"{correctAnswerChars}\" ({len(correctAnswerChars)}) is not equal to \"{self.__correctAnswers}\" ({len(self.__correctAnswers)})')

        correctAnswerChars.sort()
        return correctAnswerChars

    def getCorrectAnswerOrdinals(self) -> List[int]:
        ordinals: List[int] = list()

        index = 0
        for multipleChoiceResponse in self.__multipleChoiceResponses:
            for correctAnswer in self.__correctAnswers:
                if multipleChoiceResponse == correctAnswer:
                    ordinals.append(index)
                    break

            index = index + 1

        if not utils.hasItems(ordinals):
            raise RuntimeError(f'Couldn\'t find any correct answer ordinals within \"{self.__correctAnswers}\"!')
        elif len(ordinals) != len(self.__correctAnswers):
            raise RuntimeError(f'The length of ordinals \"{ordinals}\" ({len(ordinals)}) is not equal to \"{self.__correctAnswers}\" ({len(self.__correctAnswers)})')

        ordinals.sort()
        return ordinals

    def getPrompt(self, delimiter: str = ' ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        responsesList: List[str] = list()
        entryChar = 'A'
        for response in self.__multipleChoiceResponses:
            responsesList.append(f'[{entryChar}] {response}')
            entryChar = chr(ord(entryChar) + 1)

        responses = delimiter.join(responsesList)
        return f'{self.getQuestion()} {responses}'

    def getResponses(self) -> List[str]:
        return self.__multipleChoiceResponses


class QuestionAnswerTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[str],
        category: str,
        question: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource
    ):
        super().__init__(
            category = category,
            question = question,
            triviaDifficulty = triviaDifficulty,
            triviaSource = triviaSource,
            triviaType = TriviaType.QUESTION_ANSWER
        )

        if not utils.areValidStrs(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')

        self.__correctAnswers: List[str] = correctAnswers

    def getCorrectAnswers(self) -> List[str]:
        correctAnswers: List[str] = list()

        for correctAnswer in self.__correctAnswers:
            correctAnswers.append(correctAnswer)

        return correctAnswers

    def getPrompt(self, delimiter: str = None) -> str:
        categoryText = ''
        if self.hasCategory():
            categoryText = f' (category is \"{self.getCategory()}\")'

        return f'Jeopardy format{categoryText} — {self.getQuestion()}'

    def getResponses(self) -> List[str]:
        return list()


class TrueFalseTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[bool],
        category: str,
        question: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource
    ):
        super().__init__(
            category = category,
            question = question,
            triviaDifficulty = triviaDifficulty,
            triviaSource = triviaSource,
            triviaType = TriviaType.TRUE_FALSE
        )

        if not utils.areValidBools(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')

        self.__correctAnswers: List[bool] = correctAnswers

    def getCorrectAnswers(self) -> List[str]:
        correctAnswers: List[str] = list()

        for correctAnswer in self.__correctAnswers:
            correctAnswers.append(str(correctAnswer).lower())

        return correctAnswers

    def getCorrectAnswerBools(self) -> List[bool]:
        return self.__correctAnswers

    def getPrompt(self, delimiter: str = None) -> str:
        return f'True or false! {self.getQuestion()}'

    def getResponses(self) -> List[str]:
        return [ str(True).lower(), str(False).lower() ]
