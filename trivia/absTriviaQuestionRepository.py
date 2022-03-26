from abc import ABC, abstractmethod
from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class AbsTriviaQuestionRepository(ABC):

    def __init__(self, triviaSettingsRepository: TriviaSettingsRepository):
        if triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self._triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

    def _buildMultipleChoiceResponsesList(
        self,
        correctAnswers: List[str],
        multipleChoiceResponsesJson: List[str]
    ) -> List[str]:
        if not utils.hasItems(correctAnswers):
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')
        elif not utils.hasItems(multipleChoiceResponsesJson):
            raise ValueError(f'multipleChoiceResponsesJson argument is malformed: \"{multipleChoiceResponsesJson}\"')

        maxMultipleChoiceResponses = self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        multipleChoiceResponses: List[str] = list()

        for correctAnswer in correctAnswers:
            multipleChoiceResponses.append(correctAnswer)

        # Annoyingly, I've encountered a few situations where we can have a question with more
        # than one of the same multiple choice answers. The below logic takes some steps to make
        # sure this doesn't happen, while also ensuring that we don't have too many multiple
        # choice responses.

        for incorrectAnswer in multipleChoiceResponsesJson:
            incorrectAnswer = utils.cleanStr(incorrectAnswer, htmlUnescape = True)
            add = True

            for response in multipleChoiceResponses:
                if incorrectAnswer.lower() == response.lower():
                    add = False
                    break

            if add:
                multipleChoiceResponses.append(incorrectAnswer)

                if len(multipleChoiceResponses) >= maxMultipleChoiceResponses:
                    break

        if not utils.hasItems(multipleChoiceResponses):
            raise ValueError(f'This trivia question doesn\'t have any multiple choice responses: \"{multipleChoiceResponses}\"')

        minMultipleChoiceResponses = self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        if len(multipleChoiceResponses) < minMultipleChoiceResponses:
            raise ValueError(f'This trivia question doesn\'t have enough multiple choice responses (minimum is {minMultipleChoiceResponses}): \"{multipleChoiceResponses}\"')

        multipleChoiceResponses.sort(key = lambda response: response.lower())
        return multipleChoiceResponses

    @abstractmethod
    def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        pass
