import json
from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.recurringActionsJsonParserInterface import \
        RecurringActionsJsonParserInterface
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
except:
    import utils
    from recurringActions.recurringActionsJsonParserInterface import \
        RecurringActionsJsonParserInterface
    from recurringActions.weatherRecurringAction import WeatherRecurringAction
    from recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction


class RecurringActionsJsonParser(RecurringActionsJsonParserInterface):

    def __init__(self):
        pass

    async def parseWeather(
        self,
        isEnabled: bool,
        minutesBetween: Optional[int],
        jsonString: Optional[str],
        twitchChannel: str
    ) -> Optional[WeatherRecurringAction]:
        if not utils.isValidStr(jsonString):
            return None

        jsonContents: Optional[Dict[str, Any]] = json.loads(jsonString)
        if not utils.hasItems(jsonContents):
            return None

        # TODO

        return None

    async def parseWordOfTheDay(
        self,
        jsonString: Optional[str]
    ) -> Optional[WordOfTheDayRecurringAction]:
        if not utils.isValidStr(jsonString):
            return None

        jsonContents: Optional[Dict[str, Any]] = json.loads(jsonString)
        if not utils.hasItems(jsonContents):
            return None

        # TODO

        return None

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
