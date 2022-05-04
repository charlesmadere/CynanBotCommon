import json
import random
from asyncio import TimeoutError
from json.decoder import JSONDecodeError
from os import path
from typing import Dict

import aiohttp
from google.cloud import translate_v2 as translate

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.languagesRepository import LanguagesRepository
    from CynanBotCommon.language.translationApiSource import \
        TranslationApiSource
    from CynanBotCommon.language.translationResponse import TranslationResponse
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber

    from language.languageEntry import LanguageEntry
    from language.languagesRepository import LanguagesRepository
    from language.translationApiSource import TranslationApiSource
    from language.translationResponse import TranslationResponse


class TranslationHelper():

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        languagesRepository: LanguagesRepository,
        deepLAuthKey: str,
        timber: Timber,
        googleServiceAccountFile: str = 'CynanBotCommon/language/googleServiceAccount.json'
    ):
        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif languagesRepository is None:
            raise ValueError(f'languagesRepository argument is malformed: \"{languagesRepository}\"')
        elif not utils.isValidStr(deepLAuthKey):
            raise ValueError(f'deepLAuthKey argument is malformed: \"{deepLAuthKey}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidStr(googleServiceAccountFile):
            raise ValueError(f'googleServiceAccountFile argument is malformed: \"{googleServiceAccountFile}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__languagesRepository: LanguagesRepository = languagesRepository
        self.__deepLAuthKey: str = deepLAuthKey
        self.__timber: Timber = timber
        self.__googleServiceAccountFile: str = googleServiceAccountFile
        self.__googleTranslateClient = None

    async def __deepLTranslate(self, text: str, targetLanguageEntry: LanguageEntry) -> TranslationResponse:
        self.__timber.log('TranslationHelper', f'Fetching translation from DeepL...')

        # Retrieve translation from DeepL API: https://www.deepl.com/en/docs-api/

        requestUrl = 'https://api-free.deepl.com/v2/translate?auth_key={}&text={}&target_lang={}'.format(
            self.__deepLAuthKey, text, targetLanguageEntry.getIso6391Code())

        try:
            response = await self.__clientSession.get(requestUrl)
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('TranslationHelper', f'Encountered network error when translating \"{text}\": {e}')
            raise RuntimeError(f'Encountered network error when translating \"{text}\": {e}')

        if response.status != 200:
            self.__timber.log('TranslationHelper', f'Encountered non-200 HTTP status code when fetching translation from DeepL for \"{text}\": {response.status}')
            raise RuntimeError(f'Encountered non-200 HTTP status code when fetching translation from DeepL for \"{text}\": {response.status}')

        jsonResponse = await response.json()
        response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TranslationHelper', f'DeepL\'s JSON response is null/empty for \"{text}\": {jsonResponse}')
            raise ValueError(f'DeepL\'s JSON response is null/empty for \"{text}\": {jsonResponse}')

        translationsJson: Dict = jsonResponse.get('translations')
        if not utils.hasItems(translationsJson):
            raise RuntimeError(f'DeepL\'s JSON response for \"{text}\" has missing or empty \"translations\" field: {jsonResponse}')

        translationJson: Dict = translationsJson[0]

        originalLanguage: LanguageEntry = None
        detectedSourceLanguage: str = translationJson.get('detected_source_language')
        if utils.isValidStr(detectedSourceLanguage):
            originalLanguage = self.__languagesRepository.getLanguageForCommand(detectedSourceLanguage, hasIso6391Code = True)

        return TranslationResponse(
            originalLanguage = originalLanguage,
            translatedLanguage = targetLanguageEntry,
            originalText = text,
            translatedText = utils.getStrFromDict(translationJson, 'text', clean = True, htmlUnescape = True),
            translationApiSource = TranslationApiSource.DEEP_L
        )

    async def __getGoogleTranslateClient(self):
        if self.__googleTranslateClient is None:
            self.__timber.log('TranslationHelper', f'Initializing new Google translate.Client instance...')

            if not await self.__hasGoogleApiCredentials():
                raise RuntimeError(f'Unable to initialize a new Google translate.Client instance because the Google API credentials are missing')
            elif not path.exists(self.__googleServiceAccountFile):
                raise FileNotFoundError(f'googleServiceAccount file not found: \"{self.__googleServiceAccountFile}\"')

            self.__googleTranslateClient = translate.Client.from_service_account_json(self.__googleServiceAccountFile)

        return self.__googleTranslateClient

    async def __googleTranslate(self, text: str, targetLanguageEntry: LanguageEntry) -> TranslationResponse:
        self.__timber.log('TranslationHelper', f'Fetching translation from Google Translate...')

        translationResult = await self.__getGoogleTranslateClient().translate(
            text,
            target_language = targetLanguageEntry.getIso6391Code()
        )

        if not utils.hasItems(translationResult):
            raise RuntimeError(f'error in the data response when attempting to translate \"{text}\": {translationResult}')

        originalText: str = translationResult.get('input')
        if not utils.isValidStr(originalText):
            raise RuntimeError(f'\"input\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        translatedText: str = translationResult.get('translatedText')
        if not utils.isValidStr(translatedText):
            raise RuntimeError(f'\"translatedText\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        originalLanguage: LanguageEntry = None
        detectedSourceLanguage: str = translationResult.get('detectedSourceLanguage')
        if utils.isValidStr(detectedSourceLanguage):
            originalLanguage = self.__languagesRepository.getLanguageForCommand(detectedSourceLanguage, hasIso6391Code = True)

        return TranslationResponse(
            originalLanguage = originalLanguage,
            translatedLanguage = targetLanguageEntry,
            originalText = originalText,
            translatedText = utils.cleanStr(translatedText, htmlUnescape = True),
            translationApiSource = TranslationApiSource.GOOGLE_TRANSLATE
        )

    async def __hasGoogleApiCredentials(self) -> bool:
        if not path.exists(self.__googleServiceAccountFile):
            return False

        jsonContents: Dict[str, object] = None
        exception: JSONDecodeError = None

        with open(self.__googleServiceAccountFile, 'r') as file:
            try:
                jsonContents = json.load(file)
            except JSONDecodeError as e:
                exception = e

        return utils.hasItems(jsonContents) and exception is None

    async def translate(
        self,
        text: str,
        targetLanguageEntry: LanguageEntry = None
    ) -> TranslationResponse:
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = utils.cleanStr(text)

        if targetLanguageEntry is not None and not targetLanguageEntry.hasIso6391Code():
            raise ValueError(f'the given LanguageEntry is not supported for translation: \"{targetLanguageEntry.getName()}\"')
        elif targetLanguageEntry is None:
            targetLanguageEntry = self.__languagesRepository.requireLanguageForCommand('en', hasIso6391Code = True)

        if self.__googleTranslateClient is None and not await self.__hasGoogleApiCredentials():
            # This isn't an optimal situation, but it means that we're currently running in a
            # situation where we have no Google API credentials, but we do have DeepL credentials.
            # So here we'll just always use DeepL for translation, rather than evenly splitting
            # the workload between both services.
            return await self.__deepLTranslate(text, targetLanguageEntry)

        # In order to help keep us from running beyond the free usage tiers for the Google
        # Translate and DeepL translation services, let's randomly choose which translation service
        # to use. At the time of this writing, both services have a 500,000 character monthly limit.
        # So theoretically, this gives us a 1,000,000 character translation capability.

        translationApiSource = random.choice(list(TranslationApiSource))
        while not translationApiSource.isEnabled():
            translationApiSource = random.choice(list(TranslationApiSource))

        if translationApiSource is TranslationApiSource.DEEP_L:
            return await self.__deepLTranslate(text, targetLanguageEntry)
        elif translationApiSource is TranslationApiSource.GOOGLE_TRANSLATE:
            return await self.__googleTranslate(text, targetLanguageEntry)
        else:
            raise ValueError(f'unknown TranslationApiSource: \"{translationApiSource}\"')
