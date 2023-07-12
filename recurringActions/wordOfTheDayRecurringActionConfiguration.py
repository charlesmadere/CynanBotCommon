from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.recurringActions.absRecurringActionConfiguration import \
        AbsRecurringActionConfiguration
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
except:
    import utils
    from language.languageEntry import LanguageEntry
    from recurringActions.absRecurringActionConfiguration import \
        AbsRecurringActionConfiguration
    from recurringActions.recurringActionType import RecurringActionType


class WordOfTheDayRecurringActionConfiguration(AbsRecurringActionConfiguration):

    def __init__(self, twitchChannel: str):
        super().__init__(
            actionType = RecurringActionType.WORD_OF_THE_DAY,
            twitchChannel = twitchChannel
        )

        self.__languageEntry: Optional[LanguageEntry] = None

    def getLanguage(self) -> LanguageEntry:
        languageEntry = self.__languageEntry

        if languageEntry is None:
            raise RuntimeError(f'languageEntry value has not been set!')

        return languageEntry

    def setLanguage(self, languageEntry: LanguageEntry):
        if not isinstance(languageEntry, LanguageEntry):
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')

        self.__languageEntry = languageEntry
