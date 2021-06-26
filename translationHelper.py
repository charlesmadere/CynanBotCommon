import random
from enum import Enum, auto
from json.decoder import JSONDecodeError
from os import path

import requests
from google.cloud import translate_v2 as translate
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.languagesRepository import (LanguageEntry,
                                                    LanguagesRepository)
except:
    import utils
    from languagesRepository import LanguageEntry, LanguagesRepository


class TranslationApiSource(Enum):

    DEEP_L = auto()
    GOOGLE_TRANSLATE = auto()


class TranslationResponse():

    def __init__(
        self,
        originalLanguage: LanguageEntry,
        translatedLanguage: LanguageEntry,
        originalText: str,
        translatedText: str,
        translationApiSource: TranslationApiSource
    ):
        if not utils.isValidStr(originalText):
            raise ValueError(f'originalText argument is malformed: \"{originalText}\"')
        elif not utils.isValidStr(translatedText):
            raise ValueError(f'translatedText argument is malformed: \"{translatedText}\"')
        elif translationApiSource is None:
            raise ValueError(f'translationApiSource argument is malformed: \"{translationApiSource}\"')

        self.__originalLanguage: LanguageEntry = originalLanguage
        self.__translatedLanguage: LanguageEntry = translatedLanguage
        self.__originalText: str = originalText
        self.__translatedText: str = translatedText
        self.__translationApiSource: TranslationApiSource = translationApiSource

    def getOriginalLanguage(self) -> LanguageEntry:
        return self.__originalLanguage

    def getOriginalText(self) -> str:
        return self.__originalText

    def getTranslatedLanguage(self) -> LanguageEntry:
        return self.__translatedLanguage

    def getTranslatedText(self) -> str:
        return self.__translatedText

    def getTranslationApiSource(self) -> TranslationApiSource:
        return self.__translationApiSource

    def hasOriginalLanguage(self) -> bool:
        return self.__originalLanguage is not None

    def hasTranslatedLanguage(self) -> bool:
        return self.__translatedLanguage is not None

    def toStr(self) -> str:
        flagText = ''

        if self.hasOriginalLanguage() and self.hasTranslatedLanguage():
            firstFlagText = ''
            if self.__originalLanguage.hasFlag():
                firstFlagText = self.__originalLanguage.getFlag()
            else:
                firstFlagText = self.__originalLanguage.getIso6391Code().upper()

            secondFlagText = ''
            if self.__translatedLanguage.hasFlag():
                secondFlagText = self.__translatedLanguage.getFlag()
            else:
                secondFlagText = self.__translatedLanguage.getIso6391Code().upper()

            flagText = f'{firstFlagText} ➡ {secondFlagText} — '

        return f'{flagText}{self.__translatedText}'


class TranslationHelper():

    def __init__(
        self,
        languagesRepository: LanguagesRepository,
        deepLAuthKey: str,
        googleServiceAccountFile: str = 'CynanBotCommon/googleServiceAccount.json'
    ):
        if languagesRepository is None:
            raise ValueError(f'languagesRepository argument is malformed: \"{languagesRepository}\"')
        elif not utils.isValidStr(deepLAuthKey):
            raise ValueError(f'deepLAuthKey argument is malformed: \"{deepLAuthKey}\"')
        elif not utils.isValidStr(googleServiceAccountFile):
            raise ValueError(f'googleServiceAccountFile argument is malformed: \"{googleServiceAccountFile}\"')

        self.__languagesRepository: LanguagesRepository = languagesRepository
        self.__deepLAuthKey: str = deepLAuthKey
        self.__googleServiceAccountFile: str = googleServiceAccountFile
        self.__googleTranslateClient = None

    def __deepLTranslate(self, text: str, targetLanguageEntry: LanguageEntry) -> TranslationResponse:
        print(f'Fetching translation from DeepL... ({utils.getNowTimeText()})')

        requestUrl = 'https://api-free.deepl.com/v2/translate?auth_key={}&text={}&target_lang={}'.format(
            self.__deepLAuthKey, text, targetLanguageEntry.getIso6391Code())

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch translation for \"{text}\" from DeepL: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch translation for \"{text}\" from DeepL: {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode DeepL\'s response for \"{text}\" into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode DeepL\'s response for \"{text}\" into JSON: {e}')

        translationsJson = jsonResponse.get('translations')
        if not utils.hasItems(translationsJson):
            raise RuntimeError(f'DeepL\'s JSON response for \"{text}\" has no \"translations\" data: {jsonResponse}')

        translationJson = translationsJson[0]

        originalLanguage: LanguageEntry = None
        detectedSourceLanguage = translationJson.get('detected_source_language')
        if utils.isValidStr(detectedSourceLanguage):
            originalLanguage = self.__languagesRepository.getLanguageForCommand(detectedSourceLanguage, hasIso6391Code = True)

        return TranslationResponse(
            originalLanguage = originalLanguage,
            translatedLanguage = targetLanguageEntry,
            originalText = text,
            translatedText = utils.getStrFromDict(translationJson, 'text'),
            translationApiSource = TranslationApiSource.DEEP_L
        )

    def __getGoogleTranslateClient(self):
        if self.__googleTranslateClient is None:
            print(f'Initializing new Google translate.Client instance... ({utils.getNowTimeText()})')

            if not path.exists(self.__googleServiceAccountFile):
                raise FileNotFoundError(f'googleServiceAccount file not found: \"{self.__googleServiceAccountFile}\"')

            self.__googleTranslateClient = translate.Client.from_service_account_json(self.__googleServiceAccountFile)

        return self.__googleTranslateClient

    def __googleTranslate(self, text: str, targetLanguageEntry: LanguageEntry) -> TranslationResponse:
        print(f'Fetching translation from Google Translate... ({utils.getNowTimeText()})')

        translationResult = self.__getGoogleTranslateClient().translate(
            text,
            target_language = targetLanguageEntry.getIso6391Code()
        )

        if not utils.hasItems(translationResult):
            raise RuntimeError(f'error in the data response when attempting to translate \"{text}\": {translationResult}')

        originalText = translationResult.get('input')
        if not utils.isValidStr(originalText):
            raise RuntimeError(f'\"input\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        translatedText = translationResult.get('translatedText')
        if not utils.isValidStr(translatedText):
            raise RuntimeError(f'\"translatedText\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        originalLanguage: LanguageEntry = None
        detectedSourceLanguage = translationResult.get('detectedSourceLanguage')
        if utils.isValidStr(detectedSourceLanguage):
            originalLanguage = self.__languagesRepository.getLanguageForCommand(detectedSourceLanguage, hasIso6391Code = True)

        return TranslationResponse(
            originalLanguage = originalLanguage,
            translatedLanguage = targetLanguageEntry,
            originalText = originalText,
            translatedText = translatedText,
            translationApiSource = TranslationApiSource.GOOGLE_TRANSLATE
        )

    def translate(
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
            targetLanguageEntry = self.__languagesRepository.requireLanguageForCommand(
                command = 'en',
                hasIso6391Code = True
            )

        translationApiSource = random.choice(list(TranslationApiSource))

        if translationApiSource is TranslationApiSource.DEEP_L:
            return self.__deepLTranslate(text, targetLanguageEntry)
        elif translationApiSource is TranslationApiSource.GOOGLE_TRANSLATE:
            return self.__googleTranslate(text, targetLanguageEntry)
        else:
            raise ValueError(f'unknown TranslationApiSource: \"{translationApiSource}\"')
