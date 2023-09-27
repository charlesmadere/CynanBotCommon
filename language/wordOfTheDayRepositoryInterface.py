from abc import abstractmethod

try:
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.wordOfTheDayResponse import \
        WordOfTheDayResponse
except:
    from clearable import Clearable
    from language.languageEntry import LanguageEntry
    from language.wordOfTheDayResponse import WordOfTheDayResponse


class WordOfTheDayRepositoryInterface(Clearable):

    @abstractmethod
    async def fetchWotd(self, languageEntry: LanguageEntry) -> WordOfTheDayResponse:
        pass
