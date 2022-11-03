import json
from typing import Any, Dict, Optional

import aiofiles
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

        self.__settingsCache: Optional[Dict[str, Any]] = None

    async def clearCaches(self):
        self.__settingsCache = None

    async def isBanListEnabled(self) -> bool:
        jsonContents = await self.__readJson()
        return utils.getBoolFromDict(jsonContents, 'is_ban_list_enabled', True)

    async def getAvailableTriviaSourcesAndWeights(self) -> Dict[TriviaSource, int]:
        jsonContents = await self.__readJson()

        triviaSourcesJson: Dict[str, Any] = jsonContents['trivia_sources']
        if not utils.hasItems(triviaSourcesJson):
            raise RuntimeError(f'\"trivia_sources\" field in \"{self.__settingsFile}\" is malformed: \"{triviaSourcesJson}\"')

        triviaSources: Dict[TriviaSource, int] = dict()

        for key in triviaSourcesJson:
            triviaSource = TriviaSource.fromStr(key)
            triviaSourceJson: Dict[str, Any] = triviaSourcesJson[key]

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

    async def getLevenshteinThresholdGrowthRate(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'levenshtein_threshold_growth_rate', 7)

    async def getMaxAnswerLength(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'max_answer_length', 80)

    async def getMaxMultipleChoiceResponses(self) -> int:
        jsonContents = await self.__readJson()
        maxMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'max_multiple_choice_responses', 6)
        minMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'min_multiple_choice_responses', 2)

        if minMultipleChoiceResponses < 2:
            raise ValueError(f'min_multiple_choice_responses is too small: {minMultipleChoiceResponses}')
        elif maxMultipleChoiceResponses < minMultipleChoiceResponses:
            raise ValueError(f'min_multiple_choice_responses ({minMultipleChoiceResponses}) is less than max_multiple_choice_responses ({maxMultipleChoiceResponses})')

        return maxMultipleChoiceResponses

    async def getMaxQuestionLength(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'max_question_length', 350)

    async def getMaxPhraseAnswerLength(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'max_phrase_answer_length', 32)

    async def getMaxRetryCount(self) -> int:
        jsonContents = await self.__readJson()
        maxRetryCount = utils.getIntFromDict(jsonContents, 'max_retry_count', 5)

        if maxRetryCount < 2:
            raise ValueError(f'max_retry_count is too small: \"{maxRetryCount}\"')

        return maxRetryCount

    async def getMaxSuperGameQueueSize(self) -> int:
        jsonContents = await self.__readJson()
        maxSuperGameQueueSize = utils.getIntFromDict(jsonContents, 'max_super_game_queue_size', 25)

        if maxSuperGameQueueSize < -1:
            raise ValueError(f'max_super_game_queue_size is too small: \"{maxSuperGameQueueSize}\"')

        return maxSuperGameQueueSize

    async def getMinDaysBeforeRepeatQuestion(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'min_days_before_repeat_question', 10)

    async def getMinMultipleChoiceResponses(self) -> int:
        jsonContents = await self.__readJson()
        maxMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'max_multiple_choice_responses', 6)
        minMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'min_multiple_choice_responses', 2)

        if minMultipleChoiceResponses < 2:
            raise ValueError(f'min_multiple_choice_responses is too small: {minMultipleChoiceResponses}')
        elif maxMultipleChoiceResponses < minMultipleChoiceResponses:
            raise ValueError(f'min_multiple_choice_responses ({minMultipleChoiceResponses}) is less than max_multiple_choice_responses ({maxMultipleChoiceResponses})')

        return minMultipleChoiceResponses

    async def getSuperTriviaCooldownSeconds(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'super_trivia_cooldown_seconds', 3)

    async def getTriviaSourceInstabilityThreshold(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'trivia_source_instability_threshold', 3)

    async def isAdditionalPluralCheckingEnabled(self) -> bool:
        jsonContents = await self.__readJson()
        return utils.getBoolFromDict(jsonContents, 'additional_plural_checking_enabled', False)

    async def isDebugLoggingEnabled(self) -> bool:
        jsonContents = await self.__readJson()
        return utils.getBoolFromDict(jsonContents, 'debug_logging_enabled', False)

    async def __readJson(self) -> Dict[str, Any]:
        if self.__settingsCache:
            return self.__settingsCache

        if not await aiofiles.ospath.exists(self.__settingsFile):
            raise FileNotFoundError(f'Trivia settings file not found: \"{self.__settingsFile}\"')

        async with aiofiles.open(self.__settingsFile, mode = 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        if jsonContents is None:
            raise IOError(f'Error reading from trivia settings file: \"{self.__settingsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of trivia settings file \"{self.__settingsFile}\" is empty')

        self.__settingsCache = jsonContents
        return jsonContents
