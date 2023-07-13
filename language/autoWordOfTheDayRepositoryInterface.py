from abc import ABC, abstractmethod
from typing import Set

try:
    from CynanBotCommon.language.addAutoWordOfTheDayLanguageResult import \
        AddAutoWordOfTheDayLanguageResult
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.removeAutoWordOfTheDayLanguageResult import \
        RemoveAutoWordOfTheDayLanguageResult
except:
    from language.addAutoWordOfTheDayLanguageResult import \
        AddAutoWordOfTheDayLanguageResult
    from language.languageEntry import LanguageEntry
    from language.removeAutoWordOfTheDayLanguageResult import \
        RemoveAutoWordOfTheDayLanguageResult


class AutoWordOfTheDayRepositoryInterface(ABC):

    @abstractmethod
    async def addAutoLanguageEntry(
        self,
        languageEntry: LanguageEntry,
        twitchChannel: str
    ) -> AddAutoWordOfTheDayLanguageResult:
        pass

    @abstractmethod
    async def getAutoLanguageEntries(
        self,
        twitchChannel: str
    ) -> Set[LanguageEntry]:
        pass

    @abstractmethod
    async def removeAutoLanguageEntry(
        self,
        languageEntry: LanguageEntry,
        twitchChannel: str
    ) -> RemoveAutoWordOfTheDayLanguageResult:
        pass
