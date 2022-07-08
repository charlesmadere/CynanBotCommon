import json
from typing import Dict

import aiofile
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils

    from trivia.triviaSource import TriviaSource


class TriviaSettingsRepository():

    def __init__(
        self,
        settingsFile: str = 'CynanBotCommon/trivia/triviaSettingsRepository.json'
    ):
        if not utils.isValidStr(settingsFile):
            raise ValueError(f'settingsFile argument is malformed: \"{settingsFile}\"')

        self.__settingsFile: str = settingsFile

    async def getAvailableTriviaSourcesAndWeights(self) -> Dict[TriviaSource, int]:
        jsonContents = await self.__readJson()

        triviaSourcesJson: Dict[str, object] = jsonContents['trivia_sources']
        if not utils.hasItems(triviaSourcesJson):
            raise RuntimeError(f'\"trivia_sources\" field in \"{self.__settingsFile}\" is malformed: \"{triviaSourcesJson}\"')

        triviaSources: Dict[TriviaSource, int] = dict()

        for key in triviaSourcesJson:
            triviaSource = TriviaSource.fromStr(key)
            triviaSourceJson: Dict[str, object] = triviaSourcesJson[key]

            isEnabled = utils.getBoolFromDict(triviaSourceJson, 'is_enabled', False)
            if not isEnabled:
                continue

            weight = utils.getIntFromDict(triviaSourceJson, 'weight', 1)
            if weight < 1:
                raise ValueError(f'triviaSource \"{triviaSource}\" in \"{self.__settingsFile}\" has an invalid weight: \"{weight}\"')

            triviaSources[triviaSource] = weight

        if not utils.hasItems(triviaSources):
            raise RuntimeError(f'triviaSources is empty: \"{triviaSources}\"')

        return triviaSources

    async def getLevenshteinAnswerLengthsActivationThreshold(self) -> float:
        jsonContents = await self.__readJson()
        return utils.getFloatFromDict(jsonContents, 'levenshtein_answer_lengths_activation_threshold', 0.20)

    async def getLevenshteinAnswerLengthsRoundUpThreshold(self) -> float:
        jsonContents = await self.__readJson()
        return utils.getFloatFromDict(jsonContents, 'levenshtein_answer_lengths_round_up_threshold', 0.75)

    async def getMaxAnswerLength(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'max_answer_length', 80)

    async def getMaxLevenshteinDistance(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'max_levenshtein_distance', 1)

    async def getMaxMultipleChoiceResponses(self) -> int:
        jsonContents = await self.__readJson()

        maxMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'max_multiple_choice_responses', 5)
        minMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'min_multiple_choice_responses', 2)

        if maxMultipleChoiceResponses < 2:
            raise ValueError(f'maxMultipleChoiceResponses is too small: {maxMultipleChoiceResponses}')
        elif maxMultipleChoiceResponses < minMultipleChoiceResponses:
            raise ValueError(f'maxMultipleChoiceResponses ({maxMultipleChoiceResponses}) is less than minMultipleChoiceResponses ({minMultipleChoiceResponses})')

        return maxMultipleChoiceResponses

    async def getMaxQuestionLength(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'max_question_length', 350)

    async def getMaxPhraseAnswerLength(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'max_phrase_answer_length', 22)

    async def getMaxRetryCount(self) -> int:
        jsonContents = await self.__readJson()
        maxRetryCount = utils.getIntFromDict(jsonContents, 'max_retry_count', 5)

        if maxRetryCount < 2:
            raise ValueError(f'maxRetryCount is too small: \"{maxRetryCount}\"')

        return maxRetryCount

    async def getMinDaysBeforeRepeatQuestion(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'min_days_before_repeat_question', 10)

    async def getMinMultipleChoiceResponses(self) -> int:
        jsonContents = await self.__readJson()
        maxMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'max_multiple_choice_responses', 5)
        minMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'min_multiple_choice_responses', 2)

        if minMultipleChoiceResponses < 2:
            raise ValueError(f'minMultipleChoiceResponses is too small: \"{minMultipleChoiceResponses}\"')
        elif minMultipleChoiceResponses > maxMultipleChoiceResponses:
            raise ValueError(f'minMultipleChoiceResponses ({minMultipleChoiceResponses}) is greater than maxMultipleChoiceResponses ({maxMultipleChoiceResponses})')

        return minMultipleChoiceResponses

    async def isAdditionalPluralCheckingEnabled(self) -> bool:
        jsonContents = await self.__readJson()
        return utils.getBoolFromDict(jsonContents, 'additional_plural_checking_enabled', False)

    async def isDebugLoggingEnabled(self) -> bool:
        jsonContents = await self.__readJson()
        return utils.getBoolFromDict(jsonContents, 'debug_logging_enabled', False)

    async def __readJson(self) -> Dict[str, object]:
        if not await aiofiles.ospath.exists(self.__settingsFile):
            raise FileNotFoundError(f'Trivia settings file not found: \"{self.__settingsFile}\"')

        async with aiofile.async_open(self.__settingsFile, 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        if jsonContents is None:
            raise IOError(f'Error reading from trivia settings file: \"{self.__settingsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of trivia settings file \"{self.__settingsFile}\" is empty')

        return jsonContents
