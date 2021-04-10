import locale
import urllib
from typing import List

import requests
from lxml import html
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class JishoResult():

    def __init__(
        self,
        definitions: List[str],
        furigana: str,
        url: str,
        word: str
    ):
        if not utils.hasItems(definitions):
            raise ValueError(f'definitions argument is malformed: \"{definitions}\"')
        elif not utils.isValidUrl(url):
            raise ValueError(f'url argument is malformed: \"{url}\"')
        elif not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__definitions = definitions
        self.__furigana = furigana
        self.__url = url
        self.__word = word

    def getDefinitions(self) -> List[str]:
        return self.__definitions

    def getFurigana(self) -> str:
        return self.__furigana

    def getUrl(self) -> str:
        return self.__url

    def getWord(self) -> str:
        return self.__word

    def hasFurigana(self) -> bool:
        return utils.isValidStr(self.__furigana)

    def toStr(self, definitionDelimiter: str = ' ') -> str:
        if definitionDelimiter is None:
            raise ValueError(f'definitionDelimiter argument is malformed: \"{definitionDelimiter}\"')

        furigana = ''
        if self.hasFurigana():
            furigana = f'({self.__furigana}) '

        definitions = definitionDelimiter.join(self.__definitions)
        return f'{furigana}{self.__word} — {definitions}'


class JishoHelper():

    def __init__(self, definitionsMaxSize: int = 3):
        if not utils.isValidNum(definitionsMaxSize) or definitionsMaxSize < 1:
            raise ValueError(f'definitionsMaxSize argument is malformed: \"{definitionsMaxSize}\"')

        self.__definitionsMaxSize = definitionsMaxSize

    def search(self, query: str) -> JishoResult:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        query = query.strip()
        print(f'Looking up \"{query}\"... ({utils.getNowTimeText()})')

        encodedQuery = urllib.parse.quote(query)
        requestUrl = f'https://jisho.org/search/{encodedQuery}'

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to search Jisho for \"{query}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to search Jisho for \"{query}\": {e}')

        htmlTree = html.fromstring(rawResponse.content)
        if htmlTree is None:
            print(f'Exception occurred when attempting to decode Jisho\'s response for \"{query}\" into HTML tree')
            raise RuntimeError(f'Exception occurred when attempting to decode Jisho\'s response for \"{query}\" into HTML tree')

        parentElements = htmlTree.find_class('concept_light-representation')
        if not utils.hasItems(parentElements):
            print(f'Exception occurred when attempting to find parent elements in Jisho\'s HTML tree in query for \"{query}\"')
            raise ValueError(f'Exception occurred when attempting to find parent elements in Jisho\'s HTML tree in query for \"{query}\"')

        textElements = parentElements[0].find_class('text')
        if textElements is None or len(textElements) != 1:
            print(f'Exception occurred when attempting to find text elements in Jisho\'s HTML tree in query for \"{query}\"')
            raise ValueError(f'Exception occurred when attempting to find text elements in Jisho\'s HTML tree in query for \"{query}\"')

        word = utils.cleanStr(textElements[0].text_content())
        if not utils.isValidStr(word):
            print(f'Exception occurred when checking that Jisho\'s word is valid in query for \"{query}\"')
            raise ValueError(f'Exception occurred when checking that Jisho\'s word is valid in query for \"{query}\"')

        definitionElements = htmlTree.find_class('meaning-meaning')
        if not utils.hasItems(definitionElements):
            print(f'Exception occurred when attempting to find definition elements in Jisho\'s HTML tree in query for \"{query}\"')
            raise ValueError(f'Exception occurred when attempting to find definition elements in Jisho\'s HTML tree in query for \"{query}\"')

        definitions = list()

        for definitionElement in definitionElements:
            breakUnitElements = definitionElement.find_class('break-unit')
            if breakUnitElements is None or len(breakUnitElements) != 0:
                continue

            definition = utils.cleanStr(definitionElement.text_content())
            if not utils.isValidStr(definition):
                continue

            number = locale.format_string("%d", len(definitions) + 1, grouping = True)
            definitions.append(f'#{number} {definition}')

            if len(definitions) >= self.__definitionsMaxSize:
                # keep from adding tons of definitions
                break

        if not utils.hasItems(definitions):
            print(f'Unable to find any viable definitions for \"{query}\"')
            raise ValueError(f'Unable to find any viable definitions for \"{query}\"')

        furigana = None
        furiganaElements = htmlTree.find_class('furigana')
        if utils.hasItems(furiganaElements):
            furigana = utils.cleanStr(furiganaElements[0].text_content())

        return JishoResult(
            definitions = definitions,
            furigana = furigana,
            url = requestUrl,
            word = word
        )
