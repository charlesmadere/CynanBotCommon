import json
import os
from json.decoder import JSONDecodeError
from typing import Dict

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber


class TwitchAccessTokenMissingException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TwitchExpiresInMissingException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TwitchExpiresInOverlyAggressiveException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TwitchRefreshTokenMissingException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TwitchTokensRepository():

    def __init__(
        self,
        timber: Timber,
        isDebugLoggingEnabled: bool = False,
        tokensExpireInBuffer: int = 300,
        oauth2TokenUrl: str = 'https://id.twitch.tv/oauth2/token',
        oauth2ValidateUrl: str = 'https://id.twitch.tv/oauth2/validate',
        twitchTokensFile: str = 'CynanBotCommon/twitchTokensRepository.json'
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidBool(isDebugLoggingEnabled):
            raise ValueError(f'isDebugLoggingEnabled argument is malformed: \"{isDebugLoggingEnabled}\"')
        elif not utils.isValidNum(tokensExpireInBuffer):
            raise ValueError(f'tokensExpireInBuffer argument is malformed: \"{tokensExpireInBuffer}\"')
        elif tokensExpireInBuffer < 120:
            raise ValueError(f'tokensExpireInBuffer argument is too aggressive: {tokensExpireInBuffer}')
        elif not utils.isValidUrl(oauth2TokenUrl):
            raise ValueError(f'oauth2TokenUrl argument is malformed: \"{oauth2TokenUrl}\"')
        elif not utils.isValidUrl(oauth2ValidateUrl):
            raise ValueError(f'oauth2ValidateUrl argument is malformed: \"{oauth2ValidateUrl}\"')
        elif not utils.isValidStr(twitchTokensFile):
            raise ValueError(f'twitchTokensFile argument is malformed: \"{twitchTokensFile}\"')

        self.__timber: Timber = timber
        self.__isDebugLoggingEnabled: bool = isDebugLoggingEnabled
        self.__tokensExpireInBuffer: int = tokensExpireInBuffer
        self.__oauth2TokenUrl: str = oauth2TokenUrl
        self.__oauth2ValidateUrl: str = oauth2ValidateUrl
        self.__twitchTokensFile: str = twitchTokensFile

        self.__tokensExpireInSeconds: int = None

    def consumeTokensExpireInSeconds(self):
        self.__timber.log('TwitchTokensRepository', f'tokensExpireInSeconds value consumed, is now None')
        self.__tokensExpireInSeconds = None

    def getAccessToken(self, twitchHandle: str) -> str:
        jsonContents = self.__readJson(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'accessToken', fallback = '')

    def getRefreshToken(self, twitchHandle: str) -> str:
        jsonContents = self.__readJson(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'refreshToken', fallback = '')

    def getTokensExpireInSeconds(self) -> int:
        return self.__tokensExpireInSeconds

    def __readAllJson(self) -> Dict[str, object]:
        if not os.path.exists(self.__twitchTokensFile):
            raise FileNotFoundError(f'Twitch tokens file not found: \"{self.__twitchTokensFile}\"')

        with open(self.__twitchTokensFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Twitch tokens file: \"{self.__twitchTokensFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Twitch tokens file \"{self.__twitchTokensFile}\" is empty')

        return jsonContents

    def __readJson(self, twitchHandle: str) -> Dict[str, object]:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = self.__readAllJson()

        for key in jsonContents:
            if key.lower() == twitchHandle.lower():
                return jsonContents[key]

        # Return an empty dictionary if the given user isn't found in the Twitch tokens file. This
        # is a good bit easier to handle than throwing an exception, or something else like that.
        return dict()

    def __refreshTokens(
        self,
        twitchClientId: str,
        twitchClientSecret: str,
        twitchHandle: str
    ):
        if not utils.isValidStr(twitchClientId):
            raise ValueError(f'twitchClientId argument is malformed: \"{twitchClientId}\"')
        elif not utils.isValidStr(twitchClientSecret):
            raise ValueError(f'twitchClientSecret argument is malformed: \"{twitchClientSecret}\"')
        elif not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        self.__timber.log('TwitchTokensRepository', f'Refreshing Twitch tokens for \"{twitchHandle}\"...')

        rawResponse = None
        try:
            rawResponse = requests.post(
                url = self.__oauth2TokenUrl,
                params = {
                    'client_id': twitchClientId,
                    'client_secret': twitchClientSecret,
                    'grant_type': 'refresh_token',
                    'refresh_token': self.requireRefreshToken(twitchHandle)
                },
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TwitchTokensRepository', f'Exception occurred when attempting to request new Twitch tokens for \"{twitchHandle}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to request new Twitch tokens for \"{twitchHandle}\": {e}')

        if rawResponse.status_code != 200:
            self.__timber.log('TwitchTokensRepository', f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\": {rawResponse.status_code}')
            raise RuntimeError(f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\": {rawResponse.status_code}')

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TwitchTokensRepository', f'Exception occurred when attempting to decode new Twitch tokens response for \"{twitchHandle}\" into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode new Twitch tokens response for \"{twitchHandle}\" into JSON: {e}')

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchTokensRepository', f'Received malformed JSON response when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise ValueError(f'Received malformed JSON response when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')

        accessToken = utils.getStrFromDict(jsonResponse, 'access_token', fallback = '')
        refreshToken = utils.getStrFromDict(jsonResponse, 'refresh_token', fallback = '')
        expiresIn = utils.getIntFromDict(jsonResponse, 'expires_in', fallback = -1)

        if not utils.isValidStr(accessToken):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"access_token\" ({accessToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchAccessTokenMissingException(f'Received malformed \"access_token\" ({accessToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif not utils.isValidStr(refreshToken):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchRefreshTokenMissingException(f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif not utils.isValidNum(expiresIn):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"expires_in\" ({expiresIn}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchExpiresInMissingException(f'Received malformed \"expires_in\" ({expiresIn}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif expiresIn < 900: # 900 seconds = 15 minutes
            self.__timber.log('TwitchTokensRepository', f'Received overly aggressive \"expires_in\" ({expiresIn}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchExpiresInOverlyAggressiveException(f'Received overly aggressive \"expires_in\" ({expiresIn}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')

        if self.__isDebugLoggingEnabled:
            self.__timber.log('TwitchTokensRepository', f'JSON response for \"{twitchHandle}\" Twitch tokens refresh: {jsonResponse}')

        jsonContents = self.__readAllJson()
        jsonContents[twitchHandle] = {
            'accessToken': accessToken,
            'refreshToken': refreshToken
        }

        with open(self.__twitchTokensFile, 'w') as file:
            json.dump(jsonContents, file, indent = 4, sort_keys = True)

        if self.__tokensExpireInSeconds is None or self.__tokensExpireInSeconds > expiresIn:
            if self.__isDebugLoggingEnabled:
                self.__timber.log('TwitchTokensRepository', f'Current tokensExpireInSeconds value is {self.__tokensExpireInSeconds}, will be overwritten with {expiresIn} ({expiresIn - self.__tokensExpireInBuffer} after subtracting buffer) from \"{twitchHandle}\"')

            self.__tokensExpireInSeconds = expiresIn - self.__tokensExpireInBuffer

        self.__timber.log('TwitchTokensRepository', f'Saved new Twitch tokens for \"{twitchHandle}\" (expires in {self.__tokensExpireInSeconds} seconds)')

    def requireAccessToken(self, twitchHandle: str) -> str:
        accessToken = self.getAccessToken(twitchHandle)

        if not utils.isValidStr(accessToken):
            raise ValueError(f'\"accessToken\" value for \"{twitchHandle}\" in \"{self.__twitchTokensFile}\" is malformed: \"{accessToken}\"')

        return accessToken

    def requireRefreshToken(self, twitchHandle: str) -> str:
        refreshToken = self.getRefreshToken(twitchHandle)

        if not utils.isValidStr(refreshToken):
            raise ValueError(f'\"refreshToken\" value for \"{twitchHandle}\" in \"{self.__twitchTokensFile}\" is malformed: \"{refreshToken}\"')

        return refreshToken

    def validateAndRefreshAccessToken(
        self,
        twitchClientId: str,
        twitchClientSecret: str,
        twitchHandle: str
    ):
        if not utils.isValidStr(twitchClientId):
            raise ValueError(f'twitchClientId argument is malformed: \"{twitchClientId}\"')
        elif not utils.isValidStr(twitchClientSecret):
            raise ValueError(f'twitchClientSecret argument is malformed: \"{twitchClientSecret}\"')
        elif not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        self.__timber.log('TwitchTokensRepository', f'Validating Twitch access token for \"{twitchHandle}\"...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = self.__oauth2ValidateUrl,
                params = {
                    'Authorization': f'OAuth {self.requireAccessToken(twitchHandle)}'
                },
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TwitchTokensRepository', f'Exception occurred when attempting to validate Twitch access token: {e}')
            raise RuntimeError(f'Exception occurred when attempting to validate Twitch access token: {e}')

        # We are intentionally NOT checking the HTTP status code here.

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TwitchTokensRepository', f'Exception occurred when attempting to decode Twitch access token validation response for \"{twitchHandle}\" into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Twitch access token validation response for \"{twitchHandle}\" into JSON: {e}')

        if rawResponse.status_code != 200 or jsonResponse.get('client_id') is None or len(jsonResponse['client_id']) == 0:
            self.__refreshTokens(
                twitchClientId = twitchClientId,
                twitchClientSecret = twitchClientSecret,
                twitchHandle = twitchHandle
            )
        else:
            self.__timber.log('TwitchTokensRepository', f'No need to request new Twitch tokens for \"{twitchHandle}\"')
