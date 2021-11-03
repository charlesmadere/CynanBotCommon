from json.decoder import JSONDecodeError
from typing import List
from urllib.parse import quote

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class JishoVariant():

    def __init__(
        self,
        definitions: List[str],
        partsOfSpeech: List[str],
        furigana: str,
        word: str
    ):
        if not utils.hasItems(definitions):
            raise ValueError(f'definitions argument is malformed: \"{definitions}\"')

        self.__definitions: List[str] = definitions
        self.__partsOfSpeech: List[str] = partsOfSpeech
        self.__furigana: str = furigana
        self.__word: str = word

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

    def hasWord(self) -> str:
        return self.__word

    def toStr(self, definitionDelimiter: str = ', ') -> str:
        if definitionDelimiter is None:
            raise ValueError(f'definitionDelimiter argument is malformed: \"{definitionDelimiter}\"')

        word = ''
        if self.hasWord():
            word = self.__word

        furigana = ''
        if self.hasFurigana():
            if utils.isValidStr(word):
                furigana = f' ({self.__furigana})'
            else:
                furigana = self.__furigana

        definitionsList: List[str] = list()
        for definition in self.__definitions:
            definitionsList.append(definition)

        definitions = definitionDelimiter.join(definitionsList)
        return f'{word}{furigana} — {definitions}'


class JishoResult():

    def __init__(
        self,
        variants: List[JishoVariant],
        initialQuery: str
    ):
        if not utils.hasItems(variants):
            raise ValueError(f'variants argument is malformed: \"{variants}\"')
        elif not utils.isValidStr(initialQuery):
            raise ValueError(f'initialQuery argument is malformed: \"{initialQuery}\"')

        self.__variants: List[JishoVariant] = variants
        self.__initialQuery: str = initialQuery

    def getInitialQuery(self) -> str:
        return self.__initialQuery

    def getVariants(self) -> List[JishoVariant]:
        return self.__variants

    def toStrList(self, definitionDelimiter: str = ', ') -> List[str]:
        if definitionDelimiter is None:
            raise ValueError(f'definitionDelimiter argument is malformed: \"{definitionDelimiter}\"')

        strings: List[str] = list()
        for variant in self.__variants:
            strings.append(variant.toStr(definitionDelimiter))

        return strings


class JishoHelper():

    def __init__(self, definitionsMaxSize: int = 3, variantsMaxSize: int = 3):
        if not utils.isValidNum(definitionsMaxSize):
            raise ValueError(f'definitionsMaxSize argument is malformed: \"{definitionsMaxSize}\"')
        elif definitionsMaxSize < 1 or definitionsMaxSize > 5:
            raise ValueError(f'definitionsMaxSize argument is out of bounds: \"{definitionsMaxSize}\"')
        elif not utils.isValidNum(variantsMaxSize):
            raise ValueError(f'variantsMaxSize argument is malformed: \"{variantsMaxSize}\"')
        elif variantsMaxSize < 1 or variantsMaxSize > 3:
            raise ValueError(f'variantsMaxSize argument is out of bounds: \"{variantsMaxSize}\"')

        self.__definitionsMaxSize: int = definitionsMaxSize
        self.__variantsMaxSize: int = variantsMaxSize

    def search(self, query: str) -> JishoResult:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        query = query.strip()
        print(f'Looking up \"{query}\" at Jisho... ({utils.getNowTimeText()})')

        rawResponse = None
        try:
            encodedQuery = quote(query)
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

        variants: List[JishoVariant] = list()
        for variantJson in jsonResponse['data']:
            if not utils.hasItems(variantJson['japanese']):
                raise RuntimeError(f'Jisho\'s response for \"{query}\" has malformed or empty \"japanese\": {jsonResponse}')
            elif not utils.hasItems(variantJson['senses']):
                raise RuntimeError(f'Jisho\'s response for \"{query}\" has malformed or empty \"senses\": {jsonResponse}')

            word = utils.cleanStr(variantJson['japanese'][0].get('word', ''))
            furigana = utils.cleanStr(variantJson['japanese'][0].get('reading', ''))

            if not utils.isValidStr(word) and not utils.isValidStr(furigana):
                continue

            definitions: List[str] = list()
            for definition in variantJson['senses'][0]['english_definitions']:
                definitions.append(utils.cleanStr(definition))

                if len(definitions) >= self.__definitionsMaxSize:
                    break

            partsOfSpeech: List[str] = list()
            for partOfSpeech in variantJson['senses'][0]['parts_of_speech']:
                partsOfSpeech.append(utils.cleanStr(partOfSpeech))

                if len(partsOfSpeech) >= self.__definitionsMaxSize:
                    break

            variants.append(JishoVariant(
                definitions = definitions,
                partsOfSpeech = partsOfSpeech,
                furigana = furigana,
                word = word
            ))

            if len(variants) >= self.__variantsMaxSize:
                break

        return JishoResult(
            variants = variants,
            initialQuery = query
        )
