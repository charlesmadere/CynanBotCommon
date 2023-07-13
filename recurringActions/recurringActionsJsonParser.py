import json
from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languagesRepository import LanguagesRepository
    from CynanBotCommon.recurringActions.immutableWeatherRecurringAction import \
        ImmutableWeatherRecurringAction
    from CynanBotCommon.recurringActions.immutableWordOfTheDayRecurringAction import (
        ImmutableWordOfTheDayRecurringAction, WordOfTheDayRecurringAction)
    from CynanBotCommon.recurringActions.recurringActionsJsonParserInterface import \
        RecurringActionsJsonParserInterface
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
except:
    import utils
    from language.languagesRepository import LanguagesRepository
    from recurringActions.immutableWordOfTheDayRecurringAction import \
        ImmutableWordOfTheDayRecurringAction
    from recurringActions.recurringActionsJsonParserInterface import \
        RecurringActionsJsonParserInterface
    from recurringActions.weatherRecurringAction import WeatherRecurringAction
    from recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction


class RecurringActionsJsonParser(RecurringActionsJsonParserInterface):

    def __init__(self, languagesRepository: LanguagesRepository):
        if not isinstance(languagesRepository, LanguagesRepository):
            raise ValueError(f'languagesRepository argument is malformed: \"{languagesRepository}\"')

        self.__languagesRepository: LanguagesRepository = languagesRepository

    async def parseWeather(
        self,
        enabled: bool,
        minutesBetween: Optional[int],
        jsonString: Optional[str],
        twitchChannel: str
    ) -> Optional[WeatherRecurringAction]:
        if not utils.isValidStr(jsonString):
            return None

        jsonContents: Optional[Dict[str, Any]] = json.loads(jsonString)
        if not utils.hasItems(jsonContents):
            return None

        alertsOnly = utils.getBoolFromDict(jsonContents, 'alertsOnly')

        return ImmutableWeatherRecurringAction(
            twitchChannel = twitchChannel,
            alertsOnly = alertsOnly,
            enabled = enabled,
            minutesBetween = minutesBetween
        )

    async def parseWordOfTheDay(
        self,
        enabled: bool,
        minutesBetween: Optional[int],
        jsonString: Optional[str],
        twitchChannel: str
    ) -> Optional[WordOfTheDayRecurringAction]:
        if not utils.isValidStr(jsonString):
            return None

        jsonContents: Optional[Dict[str, Any]] = json.loads(jsonString)
        if not utils.hasItems(jsonContents):
            return None

        wotdApiCode = utils.getStrFromDict(jsonContents, 'languageEntry')
        languageEntry = await self.__languagesRepository.requireLanguageForWotdApiCode(wotdApiCode)

        return ImmutableWordOfTheDayRecurringAction(
            twitchChannel = twitchChannel,
            enabled = enabled,
            minutesBetween = minutesBetween,
            languageEntry = languageEntry
        )

    async def weatherToJson(
        self,
        weather: WeatherRecurringAction
    ) -> str:
        jsonContents: Dict[str, Any] = {
            'alertsOnly': weather.isAlertsOnly()
        }

        return json.dumps(jsonContents)

    async def wordOfTheDayToJson(
        self,
        wordOfTheDay: WordOfTheDayRecurringAction
    ) -> str:
        jsonContents: Dict[str, Any] = {
            'languageEntry': wordOfTheDay.requireLanguageEntry().getWotdApiCode()
        }

        return json.dumps(jsonContents)
