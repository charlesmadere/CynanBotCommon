import urllib
from json.decoder import JSONDecodeError
from typing import List

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class JishoResult():

    def __init__(
        self,
        definitions: List[str],
        partsOfSpeech: List[str],
        furigana: str,
        word: str
    ):
        if not utils.hasItems(definitions):
            raise ValueError(f'definitions argument is malformed: \"{definitions}\"')
        elif not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__definitions = definitions
        self.__partsOfSpeech = partsOfSpeech
        self.__furigana = furigana
        self.__word = word

    def getDefinitions(self) -> List[str]:
        return self.__definitions

    def getFurigana(self) -> str:
        return self.__furigana

    def getPartsOfSpeech(self) -> List[str]:
        return self.__partsOfSpeech

    def getWord(self) -> str:
        return self.__word

    def hasFurigana(self) -> bool:
        return utils.isValidStr(self.__furigana)

    def hasPartsOfSpeech(self) -> bool:
        return utils.hasItems(self.__partsOfSpeech)

    def toStr(self, definitionDelimiter: str = ' ') -> str:
        if definitionDelimiter is None:
            raise ValueError(f'definitionDelimiter argument is malformed: \"{definitionDelimiter}\"')

        furigana = ''
        if self.hasFurigana():
            furigana = f'({self.__furigana}) '

        definitionsList = list()
        entryChar = 'A'
        for definition in self.__definitions:
            definitionsList.append(f'[{entryChar}] {definition}')
            entryChar = chr(ord(entryChar) + 1)

        definitions = definitionDelimiter.join(definitionsList)
        return f'{furigana}{self.__word} — {definitions}'


class JishoHelper():

    def __init__(self, definitionsMaxSize: int = 3):
        if not utils.isValidNum(definitionsMaxSize):
            raise ValueError(f'definitionsMaxSize argument is malformed: \"{definitionsMaxSize}\"')
        elif definitionsMaxSize < 1:
            raise ValueError(f'definitionsMaxSize argument is out of bounds: \"{definitionsMaxSize}\"')

        self.__definitionsMaxSize = definitionsMaxSize

    def search(self, query: str) -> JishoResult:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        query = query.strip()
        print(f'Looking up \"{query}\"... ({utils.getNowTimeText()})')

        rawResponse = None
        try:
            encodedQuery = urllib.parse.quote(query)
            rawResponse = requests.get(
                url = f'https://jisho.org/api/v1/search/words?keyword={encodedQuery}',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to search Jisho for \"{query}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to search Jisho for \"{query}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Jisho\'s response for \"{query}\" into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Jisho\'s response for \"{query}\" into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            raise RuntimeError(f'Jisho\'s response for \"{query}\" has malformed or empty JSON: {jsonResponse}')
        elif 'meta' not in jsonResponse or utils.getIntFromDict(jsonResponse['meta'], 'status') != 200:
            raise RuntimeError(f'Jisho\'s response for \"{query}\" has an invalid \"status\": {jsonResponse}')
        elif not utils.hasItems(jsonResponse['data']):
            raise RuntimeError(f'Jisho\'s response for \"{query}\" has malformed or empty \"data\": {jsonResponse}')

        # The API can give us multiple results given a single search query... but for the sake
        # of simplicity, we're just grabbing one result and going with that.
        dataJson = jsonResponse['data'][0]

        if not utils.hasItems(dataJson['japanese']):
            raise RuntimeError(f'Jisho\'s response for \"{query}\" has malformed or empty \"japanese\": {jsonResponse}')
        elif not utils.hasItems(dataJson['senses']):
            raise RuntimeError(f'Jisho\'s response for \"{query}\" has malformed or empty \"senses\": {jsonResponse}')

        word = utils.getStrFromDict(dataJson['japanese'][0], 'word')
        furigana = utils.getStrFromDict(dataJson['japanese'][0], 'reading')

        definitions = list()
        for definition in dataJson['senses'][0]['english_definitions']:
            definitions.append(definition)

            if len(definitions) >= self.__definitionsMaxSize:
                break

        partsOfSpeech = list()
        for partOfSpeech in dataJson['senses'][0]['parts_of_speech']:
            partsOfSpeech.append(partOfSpeech)

            if len(partsOfSpeech) >= self.__definitionsMaxSize:
                break

        return JishoResult(
            definitions = definitions,
            partsOfSpeech = partsOfSpeech,
            furigana = furigana,
            word = word
        )
