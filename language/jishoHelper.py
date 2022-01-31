from json.decoder import JSONDecodeError
from typing import Dict, List
from urllib.parse import quote

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.jishoResult import JishoResult
    from CynanBotCommon.language.jishoVariant import JishoVariant
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber

    from language.jishoResult import JishoResult
    from language.jishoVariant import JishoVariant


class JishoHelper():

    def __init__(
        self,
        timber: Timber,
        definitionsMaxSize: int = 3,
        variantsMaxSize: int = 3
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(definitionsMaxSize):
            raise ValueError(f'definitionsMaxSize argument is malformed: \"{definitionsMaxSize}\"')
        elif definitionsMaxSize < 1 or definitionsMaxSize > 5:
            raise ValueError(f'definitionsMaxSize argument is out of bounds: \"{definitionsMaxSize}\"')
        elif not utils.isValidNum(variantsMaxSize):
            raise ValueError(f'variantsMaxSize argument is malformed: \"{variantsMaxSize}\"')
        elif variantsMaxSize < 1 or variantsMaxSize > 5:
            raise ValueError(f'variantsMaxSize argument is out of bounds: \"{variantsMaxSize}\"')

        self.__timber: Timber = timber
        self.__definitionsMaxSize: int = definitionsMaxSize
        self.__variantsMaxSize: int = variantsMaxSize

    def search(self, query: str) -> JishoResult:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        query = query.strip()
        self.__timber.log('JishoHelper', f'Looking up \"{query}\" at Jisho...')

        rawResponse = None
        try:
            encodedQuery = quote(query)
            rawResponse = requests.get(
                url = f'https://jisho.org/api/v1/search/words?keyword={encodedQuery}',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('JishoHelper', f'Exception occurred when attempting to search Jisho for \"{query}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to search Jisho for \"{query}\": {e}')

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('JishoHelper', f'Exception occurred when attempting to decode Jisho\'s response for \"{query}\" into JSON: {e}')
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
