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


class TwitchRefreshTokenMissingException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class TwitchTokensRepository():

    def __init__(
        self,
        timber: Timber,
        oauth2TokenUrl: str = 'https://id.twitch.tv/oauth2/token',
        oauth2ValidateUrl: str = 'https://id.twitch.tv/oauth2/validate',
        twitchTokensFile: str = 'CynanBotCommon/twitchTokensRepository.json'
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(oauth2TokenUrl):
            raise ValueError(f'oauth2TokenUrl argument is malformed: \"{oauth2TokenUrl}\"')
        elif not utils.isValidUrl(oauth2ValidateUrl):
            raise ValueError(f'oauth2ValidateUrl argument is malformed: \"{oauth2ValidateUrl}\"')
        elif not utils.isValidStr(twitchTokensFile):
            raise ValueError(f'twitchTokensFile argument is malformed: \"{twitchTokensFile}\"')

        self.__timber: Timber = timber
        self.__oauth2TokenUrl: str = oauth2TokenUrl
        self.__oauth2ValidateUrl: str = oauth2ValidateUrl
        self.__twitchTokensFile: str = twitchTokensFile

    def getAccessToken(self, twitchHandle: str) -> str:
        jsonContents = self.__readJson(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'accessToken', fallback = '')

    def getRefreshToken(self, twitchHandle: str) -> str:
        jsonContents = self.__readJson(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'refreshToken', fallback = '')

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
            self.__timber.log('TwitchTokensRepository', f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\"')
            raise RuntimeError(f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\"')

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TwitchTokensRepository', f'Exception occurred when attempting to decode new Twitch tokens response for \"{twitchHandle}\" into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode new Twitch tokens response for \"{twitchHandle}\" into JSON: {e}')

        if 'access_token' not in jsonResponse or len(jsonResponse['access_token']) == 0:
            raise TwitchAccessTokenMissingException(f'Received malformed \"access_token\" Twitch token: {jsonResponse}')
        elif 'refresh_token' not in jsonResponse or len(jsonResponse['refresh_token']) == 0:
            raise TwitchRefreshTokenMissingException(f'Received malformed \"refresh_token\" Twitch token: {jsonResponse}')

        jsonContents = self.__readAllJson()
        jsonContents[twitchHandle] = {
            'accessToken': jsonResponse['access_token'],
            'refreshToken': jsonResponse['refresh_token']
        }

        with open(self.__twitchTokensFile, 'w') as file:
            json.dump(jsonContents, file, indent = 4, sort_keys = True)

        self.__timber.log('TwitchTokensRepository', f'Saved new Twitch tokens for \"{twitchHandle}\"')

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

        if rawResponse.status_code != 200:
            self.__timber.log('TwitchTokensRepository', f'Encountered non-200 HTTP status code when validating Twitch access token for \"{twitchHandle}\"')
            raise RuntimeError(f'Encountered non-200 HTTP status code when validating Twitch access token for \"{twitchHandle}\"')

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TwitchTokensRepository', f'Exception occurred when attempting to decode Twitch access token validation response for \"{twitchHandle}\" into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Twitch access token validation response for \"{twitchHandle}\" into JSON: {e}')

        if jsonResponse.get('client_id') is None or len(jsonResponse['client_id']) == 0:
            self.__refreshTokens(
                twitchClientId = twitchClientId,
                twitchClientSecret = twitchClientSecret,
                twitchHandle = twitchHandle
            )
        else:
            self.__timber.log('TwitchTokensRepository', f'No need to request new Twitch tokens for \"{twitchHandle}\"')
