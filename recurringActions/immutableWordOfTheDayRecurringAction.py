from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.wordOfTheDayResponse import \
        WordOfTheDayResponse
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
except:
    import utils
    from language.languageEntry import LanguageEntry
    from language.wordOfTheDayResponse import WordOfTheDayResponse
    from recurringActions.recurringActionType import RecurringActionType
    from recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction


class ImmutableWordOfTheDayRecurringAction(WordOfTheDayRecurringAction):

    def __init__(
        self,
        twitchChannel: str,
        enabled: bool = True,
        minutesBetween: Optional[int] = None,
        languageEntry: Optional[LanguageEntry] = None,
        wordOfTheDayResponse: Optional[WordOfTheDayResponse] = None
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(enabled):
            raise ValueError(f'enabled argument is malformed: \"{enabled}\"')
        elif not utils.isValidInt(minutesBetween):
            raise ValueError(f'minutesBetween argument is malformed: \"{minutesBetween}\"')
        elif minutesBetween < 1 or minutesBetween >= utils.getIntMaxSafeSize():
            raise ValueError(f'minutesBetween argument is out of bounds: {minutesBetween}')
        elif languageEntry is not None and not isinstance(languageEntry, LanguageEntry):
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif wordOfTheDayResponse is not None and isinstance(wordOfTheDayResponse, WordOfTheDayResponse):
            raise ValueError(f'wordOfTheDayResponse argument is malformed: \"{wordOfTheDayResponse}\"')

        self.__twitchChannel: str = twitchChannel
        self.__enabled: bool = enabled
        self.__minutesBetween: Optional[int] = minutesBetween
        self.__languageEntry: Optional[LanguageEntry] = languageEntry
        self.__wordOfTheDayResponse: Optional[WordOfTheDayResponse] = wordOfTheDayResponse

    def getActionType(self) -> RecurringActionType:
        return RecurringActionType.WORD_OF_THE_DAY

    def getLanguageEntry(self) -> Optional[LanguageEntry]:
        return self.__languageEntry

    def getMinutesBetween(self) -> Optional[int]:
        return self.__minutesBetween

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def hasLanguageEntry(self) -> bool:
        return self.__languageEntry is not None

    def hasMinutesBetween(self) -> bool:
        return utils.isValidInt(self.__minutesBetween)

    def isEnabled(self) -> bool:
        return self.__enabled

    def requireLanguageEntry(self) -> LanguageEntry:
        languageEntry = self.__languageEntry

        if languageEntry is None:
            raise RuntimeError(f'No languageEntry value has been set!')

        return languageEntry

    def requireWordOfTheDayResponse(self) -> WordOfTheDayResponse:
        wordOfTheDayResponse = self.__wordOfTheDayResponse

        if wordOfTheDayResponse is None:
            raise RuntimeError(f'No wordOfTheDayResponse value has been set!')

        return wordOfTheDayResponse