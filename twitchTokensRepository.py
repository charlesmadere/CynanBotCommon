import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import aiohttp

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
        clientSession: aiohttp.ClientSession,
        timber: Timber,
        oauth2TokenUrl: str = 'https://id.twitch.tv/oauth2/token',
        oauth2ValidateUrl: str = 'https://id.twitch.tv/oauth2/validate',
        twitchTokensFile: str = 'CynanBotCommon/twitchTokensRepository.json',
        tokensExpirationBuffer: timedelta = timedelta(minutes = 10)
    ):
        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(oauth2TokenUrl):
            raise ValueError(f'oauth2TokenUrl argument is malformed: \"{oauth2TokenUrl}\"')
        elif not utils.isValidUrl(oauth2ValidateUrl):
            raise ValueError(f'oauth2ValidateUrl argument is malformed: \"{oauth2ValidateUrl}\"')
        elif not utils.isValidStr(twitchTokensFile):
            raise ValueError(f'twitchTokensFile argument is malformed: \"{twitchTokensFile}\"')
        elif tokensExpirationBuffer is None:
            raise ValueError(f'tokensExpirationBuffer argument is malformed: \"{tokensExpirationBuffer}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: Timber = timber
        self.__oauth2TokenUrl: str = oauth2TokenUrl
        self.__oauth2ValidateUrl: str = oauth2ValidateUrl
        self.__twitchTokensFile: str = twitchTokensFile
        self.__tokensExpirationBuffer: timedelta = tokensExpirationBuffer

        self.__tokenExpirations: Dict[str, datetime] = dict()

    def getAccessToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = self.__readJsonForTwitchHandle(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'accessToken', fallback = '')

    def getExpiringTwitchHandles(self) -> List[str]:
        if not utils.hasItems(self.__tokenExpirations):
            return None

        expiringTwitchHandles: List[str] = list()
        nowDateTime = datetime.now(timezone.utc)

        for twitchHandle, expirationDateTime in self.__tokenExpirations.items():
            if expirationDateTime is None or nowDateTime + self.__tokensExpirationBuffer >= expirationDateTime:
                expiringTwitchHandles.append(twitchHandle)

        return expiringTwitchHandles

    def getRefreshToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = self.__readJsonForTwitchHandle(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'refreshToken', fallback = '')

    def __isDebugLoggingEnabled(self) -> bool:
        jsonContents = self.__readAllJson()
        return utils.getBoolFromDict(jsonContents, 'debugLoggingEnabled', fallback = False)

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

    def __readJsonForTwitchHandle(self, twitchHandle: str) -> Dict[str, object]:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = self.__readAllJson()
        twitchHandlesJson: Dict[str, object] = jsonContents.get('twitchHandles')
        if not utils.hasItems(twitchHandlesJson):
            raise ValueError(f'\"twitchHandles\" JSON contents of Twitch tokens file \"{self.__twitchTokensFile}\" is missing/empty')

        for key in twitchHandlesJson:
            if key.lower() == twitchHandle.lower():
                return twitchHandlesJson[key]

        # Return an empty dictionary if the given user isn't found in the Twitch tokens file. This
        # is a good bit easier to handle than throwing an exception, or something else like that.
        return dict()

    async def __refreshTokens(
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

        response = await self.__clientSession.post(
            url = self.__oauth2TokenUrl,
            params = {
                    'client_id': twitchClientId,
                    'client_secret': twitchClientSecret,
                    'grant_type': 'refresh_token',
                    'refresh_token': self.requireRefreshToken(twitchHandle)
            }
        )

        if response.status != 200:
            self.__timber.log('TwitchTokensRepository', f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\": {response.status}')
            raise RuntimeError(f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\": {response.status}')

        jsonResponse: Dict[str, object] = await response.json()
        response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchTokensRepository', f'Received malformed JSON response when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise ValueError(f'Received malformed JSON response when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')

        accessToken = utils.getStrFromDict(jsonResponse, 'access_token', fallback = '')
        refreshToken = utils.getStrFromDict(jsonResponse, 'refresh_token', fallback = '')
        expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in', fallback = -1)

        if not utils.isValidStr(accessToken):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"access_token\" ({accessToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchAccessTokenMissingException(f'Received malformed \"access_token\" ({accessToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif not utils.isValidStr(refreshToken):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchRefreshTokenMissingException(f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif not utils.isValidNum(expiresInSeconds):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"expires_in\" ({expiresInSeconds}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchExpiresInMissingException(f'Received malformed \"expires_in\" ({expiresInSeconds}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif expiresInSeconds < 900: # 900 seconds = 15 minutes
            self.__timber.log('TwitchTokensRepository', f'Received overly aggressive \"expires_in\" ({expiresInSeconds} seconds) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchExpiresInOverlyAggressiveException(f'Received overly aggressive \"expires_in\" ({expiresInSeconds} seconds) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')

        if self.__isDebugLoggingEnabled():
            self.__timber.log('TwitchTokensRepository', f'JSON response for \"{twitchHandle}\" Twitch tokens refresh: {jsonResponse}')

        jsonContents = self.__readAllJson()
        jsonContents['twitchHandles'][twitchHandle] = {
            'accessToken': accessToken,
            'refreshToken': refreshToken
        }

        with open(self.__twitchTokensFile, 'w') as file:
            json.dump(jsonContents, file, indent = 4, sort_keys = True)

        self.__saveUserTokenExpirationTime(twitchHandle, expiresInSeconds)
        self.__timber.log('TwitchTokensRepository', f'Saved new Twitch tokens for \"{twitchHandle}\" (expiration is in {expiresInSeconds} seconds)')

    def requireAccessToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        accessToken = self.getAccessToken(twitchHandle)
        if not utils.isValidStr(accessToken):
            raise ValueError(f'\"accessToken\" value for \"{twitchHandle}\" in \"{self.__twitchTokensFile}\" is malformed: \"{accessToken}\"')

        return accessToken

    def requireRefreshToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        refreshToken = self.getRefreshToken(twitchHandle)
        if not utils.isValidStr(refreshToken):
            raise ValueError(f'\"refreshToken\" value for \"{twitchHandle}\" in \"{self.__twitchTokensFile}\" is malformed: \"{refreshToken}\"')

        return refreshToken

    def __saveUserTokenExpirationTime(self, twitchHandle: str, expiresInSeconds: int):
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')
        elif not utils.isValidNum(expiresInSeconds):
            raise ValueError(f'expiresInSeconds argument is malformed: \"{expiresInSeconds}\"')
        elif expiresInSeconds <= 0:
            raise ValueError(f'expiresInSeconds can\'t be <= 0: {expiresInSeconds}')

        nowDateTime = datetime.now(timezone.utc)
        self.__tokenExpirations[twitchHandle] = nowDateTime + timedelta(sedconds = expiresInSeconds)

    async def validateAndRefreshAccessToken(
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

        response = await self.__clientSession.get(
            url = self.__oauth2ValidateUrl,
            headers = {
                'Authorization': f'OAuth {self.requireAccessToken(twitchHandle)}'
            }
        )

        responseStatus = response.status
        jsonResponse: Dict[str, object] = await response.json()
        response.close()

        clientId: str = None
        if jsonResponse is not None and utils.isValidStr(jsonResponse.get('client_id')):
            clientId = utils.getStrFromDict(jsonResponse, 'client_id')

        expiresInSeconds: int = -1
        if jsonResponse is not None and utils.isValidNum(jsonResponse.get('expires_in')):
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in')

        if responseStatus != 200 or not utils.isValidStr(clientId) or expiresInSeconds < 900: # 900 seconds = 15 minutes
            await self.__refreshTokens(
                twitchClientId = twitchClientId,
                twitchClientSecret = twitchClientSecret,
                twitchHandle = twitchHandle
            )
        else:
            self.__saveUserTokenExpirationTime(twitchHandle, expiresInSeconds)
            self.__timber.log('TwitchTokensRepository', f'No need yet to request new Twitch tokens for \"{twitchHandle}\" (expiration is in {expiresInSeconds} seconds)')
