from datetime import timedelta
from typing import Any, Dict

import aiohttp
import xmltodict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.wordOfTheDayResponse import \
        WordOfTheDayResponse
    from CynanBotCommon.networkClientProvider import NetworkClientProvider
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.timedDict import TimedDict
except:
    import utils
    from networkClientProvider import NetworkClientProvider
    from timber.timber import Timber
    from timedDict import TimedDict

    from language.languageEntry import LanguageEntry
    from language.wordOfTheDayResponse import WordOfTheDayResponse


class WordOfTheDayRepository():

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: Timber,
        cacheTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if networkClientProvider is None:
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber
        self.__cache: TimedDict = TimedDict(timeDelta = cacheTimeDelta)

    async def clearCaches(self):
        self.__cache.clear()
        self.__timber.log('WordOfTheDayRepository', 'Caches cleared')

    async def fetchWotd(self, languageEntry: LanguageEntry) -> WordOfTheDayResponse:
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not languageEntry.hasWotdApiCode():
            raise ValueError(f'the given languageEntry is not supported for Word Of The Day: \"{languageEntry.getName()}\"')

        cacheValue = self.__cache[languageEntry.getName()]
        if cacheValue is not None:
            return cacheValue

        wotd = await self.__fetchWotd(languageEntry)
        self.__cache[languageEntry.getName()] = wotd

        return wotd

    async def __fetchWotd(self, languageEntry: LanguageEntry) -> WordOfTheDayResponse:
        if languageEntry is None:
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not languageEntry.hasWotdApiCode():
            raise ValueError(f'the given languageEntry is not supported for Word Of The Day: \"{languageEntry.getName()}\"')

        self.__timber.log('WordOfTheDayRepository', f'Fetching Word Of The Day for \"{languageEntry.getName()}\" ({languageEntry.getWotdApiCode()})...')
        clientSession = await self.__networkClientProvider.get()

        ##############################################################################
        # retrieve word of the day from https://www.transparent.com/word-of-the-day/ #
        ##############################################################################

        try:
            response = await clientSession.get(f'https://wotd.transparent.com/rss/{languageEntry.getWotdApiCode()}-widget.xml?t=0')
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('WordOfTheDayRepository', f'Encountered network error when fetching Word Of The Day for \"{languageEntry.getName()}\": {e}')
            raise RuntimeError(f'Encountered network error when fetching Word Of The Day for \"{languageEntry.getName()}\": {e}')

        if response.status != 200:
            self.__timber.log('WordOfTheDayRepository', f'Encountered non-200 HTTP status code when fetching Word Of The Day for \"{languageEntry.getName()}\" ({languageEntry.getWotdApiCode()}): {response.status}')
            raise RuntimeError(f'Encountered non-200 HTTP status code when fetching Word Of The Day for \"{languageEntry.getName()}\" ({languageEntry.getWotdApiCode()}): {response.status}')

        xmlTree = xmltodict.parse(await response.read())
        response.close()

        if not utils.hasItems(xmlTree):
            self.__timber.log('WordOfTheDayRepository', f'xmlTree for \"{languageEntry.getName()}\" is malformed: {xmlTree}')
            raise RuntimeError(f'xmlTree for \"{languageEntry.getName()}\" is malformed: {xmlTree}')

        wordsTree: Dict[str, Any] = xmlTree['xml']['words']
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
