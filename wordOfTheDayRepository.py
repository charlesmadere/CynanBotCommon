from datetime import timedelta
from typing import List

import requests
import xmltodict
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

import CynanBotCommon.utils as utils
from CynanBotCommon.timedDict import TimedDict


class LanguageEntry():

    def __init__(
        self,
        commandNames: List[str],
        apiName: str
    ):
        if not utils.hasItems(commandNames):
            raise ValueError(f'commandNames argument is malformed: \"{commandNames}\"')
        elif not utils.isValidStr(apiName):
            raise ValueError(f'apiName argument is malformed: \"{apiName}\"')

        self.__commandNames = commandNames
        self.__apiName = apiName

    def getApiName(self) -> str:
        return self.__apiName

    def getCommandNames(self) -> List[str]:
        return self.__commandNames

    def getPrimaryCommandName(self) -> str:
        return self.__commandNames[0]


class LanguageList():

    def __init__(self, entries: List[LanguageEntry]):
        if not utils.hasItems(entries):
            raise ValueError(f'entries argument is malformed: \"{entries}\"')

        self.__entries = entries

    def getLanguages(self) -> List[LanguageEntry]:
        return self.__entries

    def getLanguageForCommand(self, command: str) -> LanguageEntry:
        if not utils.isValidStr(command):
            raise ValueError(f'command argument is malformed: \"{command}\"')

        for entry in self.__entries:
            for commandName in entry.getCommandNames():
                if commandName.lower() == command.lower():
                    return entry

        raise RuntimeError(f'Unable to find language for \"{command}\"')

    def toApiNameStr(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        apiNames = list()
        for entry in self.__entries:
            apiNames.append(entry.getApiName())

        apiNames.sort()
        return delimiter.join(apiNames)

    def toCommandNamesStr(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        commandNames = list()
        for entry in self.__entries:
            commandNames.append(entry.getPrimaryCommandName())

        commandNames.sort()
        return delimiter.join(commandNames)


class Wotd():

    def __init__(
        self,
        languageEntry: LanguageEntry,
        definition: str,
        englishExample: str,
        foreignExample: str,
        languageName: str,
        transliteration: str,
        word: str
    ):
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not utils.isValidStr(definition):
            raise ValueError(f'definition argument is malformed: \"{definition}\"')
        elif not utils.isValidStr(languageName):
            raise ValueError(f'languageName argument is malformed: \"{languageName}\"')
        elif not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__languageEntry = languageEntry
        self.__definition = definition
        self.__englishExample = englishExample
        self.__foreignExample = foreignExample
        self.__languageName = languageName
        self.__transliteration = transliteration
        self.__word = word

    def getDefinition(self) -> str:
        return self.__definition

    def getEnglishExample(self) -> str:
        return self.__englishExample

    def getForeignExample(self) -> str:
        return self.__foreignExample

    def getLanguageEntry(self) -> LanguageEntry:
        return self.__languageEntry

    def getLanguageName(self) -> str:
        return self.__languageName

    def getTransliteration(self) -> str:
        return self.__transliteration

    def getWord(self) -> str:
        return self.__word

    def hasExamples(self) -> bool:
        return utils.isValidStr(self.__englishExample) and utils.isValidStr(self.__foreignExample)

    def hasTransliteration(self) -> bool:
        return utils.isValidStr(self.__transliteration)

    def toStr(self) -> str:
        if self.hasExamples():
            if self.hasTransliteration():
                return f'({self.getLanguageName()}) {self.getWord()} ({self.getTransliteration()}) — {self.getDefinition()}. Example: {self.getForeignExample()} {self.getEnglishExample()}'
            else:
                return f'({self.getLanguageName()}) {self.getWord()} — {self.getDefinition()}. Example: {self.getForeignExample()} {self.getEnglishExample()}'
        elif self.hasTransliteration():
            return f'({self.getLanguageName()}) {self.getWord()} ({self.getTransliteration()}) — {self.getDefinition()}'
        else:
            return f'({self.getLanguageName()}) {self.getWord()} — {self.getDefinition()}'


class WordOfTheDayRepository():

    def __init__(
        self,
        cacheTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__cache = TimedDict(timeDelta = cacheTimeDelta)
        self.__languageList = self.__createLanguageList()

    def __createLanguageList(self) -> LanguageList:
        entries = list()

        entries.append(LanguageEntry(
            apiName = 'de',
            commandNames = [ 'de', 'german', 'germany' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'en-es',
            commandNames = [ 'en-es' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'en-pt',
            commandNames = [ 'en-pt' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'es',
            commandNames = [ 'es', 'spanish' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'fr',
            commandNames = [ 'fr', 'french', 'france' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'it',
            commandNames = [ 'it', 'italian', 'italy' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'ja',
            commandNames = [ 'ja', 'japanese', 'jp', 'japan' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'korean',
            commandNames = [ 'ko', 'korean', 'korea' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'nl',
            commandNames = [ 'nl', 'dutch' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'norwegian',
            commandNames = [ 'no', 'norwegian' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'polish',
            commandNames = [ 'po', 'polish', 'poland' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'pt',
            commandNames = [ 'pt', 'portuguese' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'ru',
            commandNames = [ 'ru', 'russian', 'russia' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'swedish',
            commandNames = [ 'sv', 'swedish', 'sw', 'sweden' ]
        ))

        entries.append(LanguageEntry(
            apiName = 'zh',
            commandNames = [ 'zh', 'chinese', 'china' ]
        ))

        return LanguageList(entries = entries)

    def fetchWotd(self, languageEntry: LanguageEntry) -> Wotd:
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')

        cacheValue = self.__cache[languageEntry]
        if cacheValue is not None:
            return cacheValue

        wotd = self.__fetchWotd(languageEntry)
        self.__cache[languageEntry] = wotd

        return wotd

    def __fetchWotd(self, languageEntry: LanguageEntry) -> Wotd:
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')

        cacheValue = self.__cache[languageEntry]

        if cacheValue is not None:
            return cacheValue

        print(f'Refreshing Word Of The Day for \"{languageEntry.getApiName()}\"... ({utils.getNowTimeText()})')

        ##############################################################################
        # retrieve word of the day from https://www.transparent.com/word-of-the-day/ #
        ##############################################################################

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = f'https://wotd.transparent.com/rss/{languageEntry.getApiName()}-widget.xml?t=0',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch Word Of The Day for \"{languageEntry.getApiName()}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Word Of The Day for \"{languageEntry.getApiName()}\": {e}')

        xmlTree = xmltodict.parse(rawResponse.content)
        if not utils.hasItems(xmlTree):
            print(f'xmlTree for \"{languageEntry.getApiName()}\" is malformed: {xmlTree}')
            raise RuntimeError(f'xmlTree for \"{languageEntry.getApiName()}\" is malformed: {xmlTree}')

        wordsTree = xmlTree['xml']['words']
        word = wordsTree['word']
        definition = wordsTree['translation']
        englishExample = wordsTree.get('enphrase')
        foreignExample = wordsTree.get('fnphrase')
        languageName = wordsTree['langname']
        transliteration = wordsTree.get('wotd:transliteratedWord')

        return Wotd(
            languageEntry = languageEntry,
            word = word,
            definition = definition,
            englishExample = englishExample,
            languageName = languageName,
            foreignExample = foreignExample,
            transliteration = transliteration
        )

    def getLanguageList(self) -> LanguageList:
        return self.__languageList
