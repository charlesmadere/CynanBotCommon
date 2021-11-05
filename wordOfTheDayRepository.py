from datetime import timedelta

import requests
import xmltodict
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.timedDict import TimedDict
except:
    import utils
    from language.languageEntry import LanguageEntry
    from timedDict import TimedDict


class Wotd():

    def __init__(
        self,
        languageEntry: LanguageEntry,
        definition: str,
        englishExample: str,
        foreignExample: str,
        transliteration: str,
        word: str
    ):
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not utils.isValidStr(definition):
            raise ValueError(f'definition argument is malformed: \"{definition}\"')
        elif not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__languageEntry: LanguageEntry = languageEntry
        self.__definition: str = definition
        self.__englishExample: str = englishExample
        self.__foreignExample: str = foreignExample
        self.__transliteration: str = transliteration
        self.__word: str = word

    def getDefinition(self) -> str:
        return self.__definition

    def getEnglishExample(self) -> str:
        return self.__englishExample

    def getForeignExample(self) -> str:
        return self.__foreignExample

    def getLanguageEntry(self) -> LanguageEntry:
        return self.__languageEntry

    def getLanguageName(self) -> str:
        return self.__languageEntry.getName()

    def getTransliteration(self) -> str:
        return self.__transliteration

    def getWord(self) -> str:
        return self.__word

    def hasExamples(self) -> bool:
        return utils.isValidStr(self.__englishExample) and utils.isValidStr(self.__foreignExample)

    def hasTransliteration(self) -> bool:
        return utils.isValidStr(self.__transliteration)

    def toStr(self) -> str:
        languageNameAndFlag = None
        if self.__languageEntry.hasFlag():
            languageNameAndFlag = f'{self.__languageEntry.getFlag()} {self.getLanguageName()}'
        else:
            languageNameAndFlag = self.getLanguageName()

        if self.hasExamples():
            if self.hasTransliteration():
                return f'{languageNameAndFlag} — {self.getWord()} ({self.getTransliteration()}) — {self.getDefinition()}. Example: {self.getForeignExample()} {self.getEnglishExample()}'
            else:
                return f'{languageNameAndFlag} — {self.getWord()} — {self.getDefinition()}. Example: {self.getForeignExample()} {self.getEnglishExample()}'
        elif self.hasTransliteration():
            return f'{languageNameAndFlag} — {self.getWord()} ({self.getTransliteration()}) — {self.getDefinition()}'
        else:
            return f'{languageNameAndFlag} — {self.getWord()} — {self.getDefinition()}'


class WordOfTheDayRepository():

    def __init__(
        self,
        cacheTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__cache: TimedDict = TimedDict(timeDelta = cacheTimeDelta)

    def fetchWotd(self, languageEntry: LanguageEntry) -> Wotd:
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not languageEntry.hasWotdApiCode():
            raise ValueError(f'the given languageEntry is not supported for Word Of The Day: \"{languageEntry.getName()}\"')

        cacheValue = self.__cache[languageEntry]
        if cacheValue is not None:
            return cacheValue

        wotd = self.__fetchWotd(languageEntry)
        self.__cache[languageEntry] = wotd

        return wotd

    def __fetchWotd(self, languageEntry: LanguageEntry) -> Wotd:
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not languageEntry.hasWotdApiCode():
            raise ValueError(f'the given languageEntry is not supported for Word Of The Day: \"{languageEntry.getName()}\"')

        print(f'Fetching Word Of The Day for \"{languageEntry.getName()}\"... ({utils.getNowTimeText()})')

        ##############################################################################
        # retrieve word of the day from https://www.transparent.com/word-of-the-day/ #
        ##############################################################################

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = f'https://wotd.transparent.com/rss/{languageEntry.getWotdApiCode()}-widget.xml?t=0',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch Word Of The Day for \"{languageEntry.getName()}\" ({languageEntry.getWotdApiCode()}): {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Word Of The Day for \"{languageEntry.getName()}\" ({languageEntry.getWotdApiCode()}): {e}')

        xmlTree = xmltodict.parse(rawResponse.content)
        if not utils.hasItems(xmlTree):
            print(f'xmlTree for \"{languageEntry.getName()}\" is malformed: {xmlTree}')
            raise RuntimeError(f'xmlTree for \"{languageEntry.getName()}\" is malformed: {xmlTree}')

        wordsTree = xmlTree['xml']['words']
        word = utils.getStrFromDict(wordsTree, 'word', clean = True)
        definition = utils.getStrFromDict(wordsTree, 'translation', clean = True)
        englishExample = utils.getStrFromDict(wordsTree, 'enphrase', fallback = '', clean = True)
        foreignExample = utils.getStrFromDict(wordsTree, 'fnphrase', fallback = '', clean = True)
        transliteration = utils.getStrFromDict(wordsTree, 'wotd:transliteratedWord', fallback = '', clean = True)

        return Wotd(
            languageEntry = languageEntry,
            word = word,
            definition = definition,
            englishExample = englishExample,
            foreignExample = foreignExample,
            transliteration = transliteration
        )
