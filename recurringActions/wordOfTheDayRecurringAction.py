from abc import abstractmethod
from typing import Optional

try:
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.wordOfTheDayResponse import \
        WordOfTheDayResponse
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
except:
    from language.languageEntry import LanguageEntry
    from language.wordOfTheDayResponse import WordOfTheDayResponse
    from recurringActions.recurringAction import RecurringAction


class WordOfTheDayRecurringAction(RecurringAction):

    @abstractmethod
    def getLanguageEntry(self) -> Optional[LanguageEntry]:
        pass

    @abstractmethod
    def hasLanguageEntry(self) -> bool:
        pass

    @abstractmethod
    def requireLanguageEntry(self) -> LanguageEntry:
        pass

    @abstractmethod
    def requireWordOfTheDayResponse(self) -> WordOfTheDayResponse:
        pass
