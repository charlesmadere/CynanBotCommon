from abc import abstractmethod
from typing import Optional

try:
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
except:
    from language.languageEntry import LanguageEntry
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
