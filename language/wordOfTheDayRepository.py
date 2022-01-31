from datetime import timedelta

import requests
import xmltodict
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.wordOfTheDayResponse import \
        WordOfTheDayResponse
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.timedDict import TimedDict
except:
    import utils
    from timber.timber import Timber
    from timedDict import TimedDict

    from language.languageEntry import LanguageEntry
    from language.wordOfTheDayResponse import WordOfTheDayResponse


class WordOfTheDayRepository():

    def __init__(
        self,
        timber: Timber,
        cacheTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__timber: Timber = timber
        self.__cache: TimedDict = TimedDict(timeDelta = cacheTimeDelta)

    def fetchWotd(self, languageEntry: LanguageEntry) -> WordOfTheDayResponse:
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

    def __fetchWotd(self, languageEntry: LanguageEntry) -> WordOfTheDayResponse:
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not languageEntry.hasWotdApiCode():
            raise ValueError(f'the given languageEntry is not supported for Word Of The Day: \"{languageEntry.getName()}\"')

        self.__timber.log('WordOfTheDayRepository', f'Fetching Word Of The Day for \"{languageEntry.getName()}\"...')

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
            self.__timber.log('WordOfTheDayRepository', f'Exception occurred when attempting to fetch Word Of The Day for \"{languageEntry.getName()}\" ({languageEntry.getWotdApiCode()}): {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Word Of The Day for \"{languageEntry.getName()}\" ({languageEntry.getWotdApiCode()}): {e}')

        xmlTree = xmltodict.parse(rawResponse.content)
        if not utils.hasItems(xmlTree):
            self.__timber.log('WordOfTheDayRepository', f'xmlTree for \"{languageEntry.getName()}\" is malformed: {xmlTree}')
            raise RuntimeError(f'xmlTree for \"{languageEntry.getName()}\" is malformed: {xmlTree}')

        wordsTree = xmlTree['xml']['words']
        word = utils.getStrFromDict(wordsTree, 'word', clean = True)
        definition = utils.getStrFromDict(wordsTree, 'translation', clean = True)
        englishExample = utils.getStrFromDict(wordsTree, 'enphrase', fallback = '', clean = True)
        foreignExample = utils.getStrFromDict(wordsTree, 'fnphrase', fallback = '', clean = True)
        transliteration = utils.getStrFromDict(wordsTree, 'wotd:transliteratedWord', fallback = '', clean = True)

        return WordOfTheDayResponse(
            languageEntry = languageEntry,
            word = word,
            definition = definition,
            englishExample = englishExample,
            foreignExample = foreignExample,
            transliteration = transliteration
        )
