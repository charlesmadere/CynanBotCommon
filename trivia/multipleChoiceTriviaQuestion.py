from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class MultipleChoiceTriviaQuestion(AbsTriviaQuestion):

    def __init__(
        self,
        correctAnswers: List[str],
        multipleChoiceResponses: List[str],
        category: str,
        question: str,
        triviaId: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource
    ):
        super().__init__(
            category = category,
            question = question,
            triviaId = triviaId,
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

    def getCorrectAnswers(self) -> List[str]:
        answerStrings: List[str] = list()
        index: int = 0

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

        responses = delimiter.join(responsesList)
        return f'{self.getQuestion()} {responses}'

    def getResponses(self) -> List[str]:
        return self.__multipleChoiceResponses
