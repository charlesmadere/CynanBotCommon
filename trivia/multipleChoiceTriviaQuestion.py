from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaExceptions import (
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException)
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaExceptions import (
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException)
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class MultipleChoiceTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[str],
        multipleChoiceResponses: List[str],
        category: Optional[str],
        categoryId: Optional[str],
        emote: str,
        question: str,
        triviaId: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource
    ):
        super().__init__(
            category = category,
            categoryId = categoryId,
            emote = emote,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = triviaDifficulty,
            triviaSource = triviaSource,
            triviaType = TriviaType.MULTIPLE_CHOICE,
        )

        if not utils.areValidStrs(correctAnswers):
            raise NoTriviaCorrectAnswersException(f'correctAnswers argument is malformed: \"{correctAnswers}\"')
        elif not utils.hasItems(multipleChoiceResponses):
            raise NoTriviaMultipleChoiceResponsesException(f'multipleChoiceResponses argument is malformed: \"{multipleChoiceResponses}\"')

        self.__correctAnswers: List[str] = correctAnswers
        self.__multipleChoiceResponses: List[str] = multipleChoiceResponses

    def getAnswerOrdinals(self) -> List[int]:
        answerOrdinals: List[int] = list()

        for index in range(0, len(self.__multipleChoiceResponses)):
            answerOrdinals.append(index)

        return answerOrdinals

    def getCorrectAnswers(self) -> List[str]:
        answerStrings: List[str] = list()

        for index, correctAnswerChar in enumerate(self.getCorrectAnswerChars()):
            answerStrings.append(f'[{correctAnswerChar}] {self.__correctAnswers[index]}')

        return answerStrings

    def getCorrectAnswerChars(self) -> List[str]:
        correctAnswerOrdinals = self.getCorrectAnswerOrdinals()
        correctAnswerChars: List[str] = list()

        for ordinal in correctAnswerOrdinals:
            correctAnswerChars.append(chr(ord('A') + ordinal))

        if not utils.hasItems(correctAnswerChars):
            raise RuntimeError(f'Couldn\'t find any correct answer chars within \"{self.__correctAnswers}\"')
        elif len(correctAnswerChars) != len(self.__correctAnswers):
            raise RuntimeError(f'The length of correctAnswerChars \"{correctAnswerChars}\" ({len(correctAnswerChars)}) is not equal to \"{self.__correctAnswers}\" ({len(self.__correctAnswers)})')

        correctAnswerChars.sort()
        return correctAnswerChars

    def getCorrectAnswerOrdinals(self) -> List[int]:
        ordinals: List[int] = list()

        for index, multipleChoiceResponse in enumerate(self.__multipleChoiceResponses):
            for correctAnswer in self.__correctAnswers:
                if multipleChoiceResponse == correctAnswer:
                    ordinals.append(index)
                    break

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

        responsesStr = delimiter.join(responsesList)
        return f'{self.getQuestion()} {responsesStr}'

    def getResponses(self) -> List[str]:
        return utils.copyList(self.__multipleChoiceResponses)
