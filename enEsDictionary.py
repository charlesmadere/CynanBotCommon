import locale
import urllib
from json.decoder import JSONDecodeError
from typing import List

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class EnEsDictionaryResult():

    def __init__(self, definitions: List[str], word: str):
        if not utils.hasItems(definitions):
            raise ValueError(f'definitions argument is malformed: \"{definitions}\"')
        elif not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__definitions = definitions
        self.__word = word

    def getDefinitions(self) -> List[str]:
        return self.__definitions

    def getWord(self) -> str:
        return self.__word

    def toStr(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        definitionsJoin = delimiter.join(self.__definitions)
        return f'{self.__word} — {definitionsJoin}'


class EnEsDictionary():

    def __init__(
        self,
        merriamWebsterApiKey: str,
        definitionsMaxSize: int = 3
    ):
        if not utils.isValidStr(merriamWebsterApiKey):
            raise ValueError(f'merriamWebsterApiKey argument is malformed: \"{merriamWebsterApiKey}\"')
        elif not utils.isValidNum(definitionsMaxSize) or definitionsMaxSize < 1:
            raise ValueError(f'definitionsMaxSize argument is malformed: \"{definitionsMaxSize}\"')

        self.__definitionsMaxSize = definitionsMaxSize
        self.__merriamWebsterApiKey = merriamWebsterApiKey

    def search(self, query: str) -> EnEsDictionaryResult:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        query = query.strip()
        print(f'Looking up \"{query}\"... ({utils.getNowTimeText()})')

        encodedQuery = urllib.parse.quote(query)
        requestUrl = 'https://www.dictionaryapi.com/api/v3/references/spanish/json/{}?key={}'.format(
            encodedQuery, self.__merriamWebsterApiKey)

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to search Merriam Webster for \"{query}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to search Merriam Webster for \"{query}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Merriam Webster\'s response into JSON for \"{query}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Merriam Webster\'s response into JSON for \"{query}\": {e}')

        if not utils.hasItems(jsonResponse):
            print(f'jsonResponse for \"{query}\" has no definitions: {jsonResponse}')
            raise ValueError(f'jsonResponse \"{query}\" has no definitions: {jsonResponse}')

        definitions = list()

        for entry in jsonResponse:
            definition = None

            if isinstance(entry, str):
                definition = entry
            elif not entry['meta'].get('offensive', True) and utils.hasItems(entry['shortdef']):
                definition = entry['shortdef'][0]

            definition = utils.cleanStr(definition)
            if not utils.isValidStr(definition):
                continue

            index = 0
            add = True

            while (index < len(definitions) and add):
                if definitions[index].lower() == definition.lower():
                    add = False

                index = index + 1

            if add:
                number = locale.format_string("%d", len(definitions) + 1, grouping = True)
                definitions.append(f'#{number} {definition}')

                if len(definitions) >= self.__definitionsMaxSize:
                    # keep from adding tons of definitions
                    break

        if not utils.hasItems(definitions):
            print(f'Unable to find any viable definitions for \"{query}\"')
            raise ValueError(f'Unable to find any viable definitions for \"{query}\"')

        return EnEsDictionaryResult(
            definitions = definitions,
            word = query
        )
