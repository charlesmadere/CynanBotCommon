import json
import random
from os import path
from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.triviaModels import (AbsTriviaQuestion,
                                             MultipleChoiceTriviaQuestion,
                                             QuestionAnswerTriviaQuestion,
                                             TriviaDifficulty, TriviaSource,
                                             TriviaType,
                                             TrueFalseTriviaQuestion)
except:
    import utils
    from triviaModels import (AbsTriviaQuestion, MultipleChoiceTriviaQuestion,
                              QuestionAnswerTriviaQuestion, TriviaDifficulty,
                              TriviaSource, TriviaType,
                              TrueFalseTriviaQuestion)


class LocalTriviaRepository():

    def __init__(
        self,
        localTriviaFile: str = 'CynanBotCommon/localTriviaRepository.json'
    ):
        if not utils.isValidStr(localTriviaFile):
            raise ValueError(f'localTriviaFile argument is malformed: \"{localTriviaFile}\"')

        self.__localTriviaFile: str = localTriviaFile

    def fetchRandomQuestion(self) -> AbsTriviaQuestion:
        questionJson = self.__fetchRandomQuestionJson()

        category = utils.getStrFromDict(questionJson, 'category', fallback = '', clean = True)
        question = utils.getStrFromDict(questionJson, 'question', clean = True)

        triviaDifficulty = TriviaDifficulty.fromStr(questionJson.get('difficulty'))
        triviaType = TriviaType.fromStr(utils.getStrFromDict(questionJson, 'type'))

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswers: List[str] = questionJson['correctAnswers']
            multipleChoiceResponses: List[str] = questionJson['responses']
            random.shuffle(multipleChoiceResponses)

            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                question = question,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.LOCAL_TRIVIA_REPOSITORY
            )
        elif triviaType is TriviaType.QUESTION_ANSWER:
            correctAnswers: List[str] = questionJson['correctAnswers']

            return QuestionAnswerTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                question = question,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.LOCAL_TRIVIA_REPOSITORY
            )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswers: List[bool] = questionJson['correctAnswers']

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                question = question,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.LOCAL_TRIVIA_REPOSITORY
            )
        else:
            raise ValueError(f'triviaType \"{triviaType}\" is unknown for Local Trivia Repository: {questionJson}')

    def __fetchRandomQuestionJson(self) -> Dict:
        jsonContents = self.__readJson()
        return random.choice(jsonContents)

    def __readJson(self) -> List:
        if not path.exists(self.__localTriviaFile):
            raise FileNotFoundError(f'Local Trivia file not found: \"{self.__localTriviaFile}\"')

        with open(self.__localTriviaFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Local Trivia file: \"{self.__localTriviaFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Local Trivia file \"{self.__localTriviaFile}\" is empty')

        return jsonContents
