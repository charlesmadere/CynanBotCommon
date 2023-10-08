import traceback
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.exceptions import (
        TwitchAccessTokenMissingException, TwitchErrorException,
        TwitchJsonException, TwitchPasswordChangedException,
        TwitchRefreshTokenMissingException, TwitchTokenIsExpiredException)
    from CynanBotCommon.twitch.twitchApiServiceInterface import \
        TwitchApiServiceInterface
    from CynanBotCommon.twitch.twitchBroadcasterType import \
        TwitchBroadcasterType
    from CynanBotCommon.twitch.twitchCredentialsProviderInterface import \
        TwitchCredentialsProviderInterface
    from CynanBotCommon.twitch.twitchEmoteDetails import TwitchEmoteDetails
    from CynanBotCommon.twitch.twitchEmoteImage import TwitchEmoteImage
    from CynanBotCommon.twitch.twitchEmoteImageScale import \
        TwitchEmoteImageScale
    from CynanBotCommon.twitch.twitchEmoteType import TwitchEmoteType
    from CynanBotCommon.twitch.twitchLiveUserDetails import \
        TwitchLiveUserDetails
    from CynanBotCommon.twitch.twitchStreamType import TwitchStreamType
    from CynanBotCommon.twitch.twitchSubscriberTier import TwitchSubscriberTier
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
    from CynanBotCommon.twitch.twitchUserDetails import TwitchUserDetails
    from CynanBotCommon.twitch.twitchUserSubscriptionDetails import \
        TwitchUserSubscriptionDetails
    from CynanBotCommon.twitch.twitchUserType import TwitchUserType
except:
    import utils
    from network.exceptions import GenericNetworkException
    from network.networkClientProvider import NetworkClientProvider
    from timber.timberInterface import TimberInterface

    from twitch.exceptions import (TwitchAccessTokenMissingException,
                                   TwitchErrorException, TwitchJsonException,
                                   TwitchPasswordChangedException,
                                   TwitchRefreshTokenMissingException,
                                   TwitchTokenIsExpiredException)
    from twitch.twitchApiServiceInterface import TwitchApiServiceInterface
    from twitch.twitchBroadcasterType import TwitchBroadcasterType
    from twitch.twitchCredentialsProviderInterface import \
        TwitchCredentialsProviderInterface
    from twitch.twitchEmoteDetails import TwitchEmoteDetails
    from twitch.twitchEmoteImage import TwitchEmoteImage
    from twitch.twitchEmoteImageScale import TwitchEmoteImageScale
    from twitch.twitchEmoteType import TwitchEmoteType
    from twitch.twitchLiveUserDetails import TwitchLiveUserDetails
    from twitch.twitchStreamType import TwitchStreamType
    from twitch.twitchSubscriberTier import TwitchSubscriberTier
    from twitch.twitchTokensDetails import TwitchTokensDetails
    from twitch.twitchUserDetails import TwitchUserDetails
    from twitch.twitchUserSubscriptionDetails import \
        TwitchUserSubscriptionDetails
    from twitch.twitchUserType import TwitchUserType


class TwitchApiService(TwitchApiServiceInterface):

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: TimberInterface,
        twitchCredentialsProvider: TwitchCredentialsProviderInterface,
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(networkClientProvider, NetworkClientProvider):
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchCredentialsProvider, TwitchCredentialsProviderInterface):
            raise ValueError(f'twitchCredentialsProvider argument is malformed: \"{twitchCredentialsProvider}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: TimberInterface = timber
        self.__twitchCredentialsProvider: TwitchCredentialsProviderInterface = twitchCredentialsProvider
        self.__timeZone: timezone = timeZone

    async def __calculateExpirationTime(self, expiresInSeconds: Optional[int]) -> datetime:
        nowDateTime = datetime.now(self.__timeZone)

        if utils.isValidInt(expiresInSeconds) and expiresInSeconds > 0:
            return nowDateTime + timedelta(seconds = expiresInSeconds)
        else:
            return nowDateTime - timedelta(weeks = 1)

    async def fetchEmoteDetails(
        self,
        broadcasterId: str,
        twitchAccessToken: str
    ) -> List[TwitchEmoteDetails]:
        if not utils.isValidStr(broadcasterId):
            raise ValueError(f'broadcasterId argument is malformed: \"{broadcasterId}\"')
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        self.__timber.log('TwitchApiService', f'Fetching emote details... (broadcasterId=\"{broadcasterId}\")')
        twitchClientId = await self.__twitchCredentialsProvider.getTwitchClientId()
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = f'https://api.twitch.tv/helix/emotes?broadcaster_id={broadcasterId}',
                headers = {
                    'Authorization': f'Bearer {twitchAccessToken}',
                    'Client-Id': twitchClientId
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching emote details (broadcasterId=\"{broadcasterId}\"): {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchApiService encountered network error when fetching emote details (broadcasterId=\"{broadcasterId}\"): {e}')

        responseStatusCode = response.getStatusCode()
        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiService', f'Received a null/empty JSON response when fetching emote details (broadcasterId=\"{broadcasterId}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty JSON response when fetching emote details (broadcasterId=\"{broadcasterId}\"): {jsonResponse}')
        elif responseStatusCode == 401 or ('error' in jsonResponse and len(jsonResponse['error']) >= 1):
            self.__timber.log('TwitchApiService', f'Received an error ({responseStatusCode}) when fetching emote details (broadcasterId=\"{broadcasterId}\"): {jsonResponse}')
            raise TwitchTokenIsExpiredException(f'TwitchApiService received an error ({responseStatusCode}) when fetching emote details (broadcasterId=\"{broadcasterId}\"): {jsonResponse}')
        elif responseStatusCode != 200:
            self.__timber.log('TwitchApiService', f'Encountered non-200 HTTP status code when fetching emote details (broadcasterId=\"{broadcasterId}\"): {responseStatusCode}')
            raise GenericNetworkException(f'TwitchApiService encountered non-200 HTTP status code when fetching emote details (broadcasterId=\"{broadcasterId}\"): {responseStatusCode}')

        data: Optional[List[Dict[str, Any]]] = jsonResponse.get('data')
        if not utils.hasItems(data):
            self.__timber.log('TwitchApiService', f'Received a null/empty \"data\" field in the JSON response when fetching emote details (broadcasterId=\"{broadcasterId}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty \"data\" field in the JSON response when fetching emote details (broadcasterId=\"{broadcasterId}\"): {jsonResponse}')

        emoteDetailsList: List[TwitchEmoteDetails] = list()

        for emoteJson in data:
            imagesJson: Dict[str, str] = emoteJson['images']
            emoteImages: List[TwitchEmoteImage] = list()

            for imageJsonKey, imageJsonValue in imagesJson:
                emoteImages.append(TwitchEmoteImage(
                    url = imageJsonKey,
                    imageScale = TwitchEmoteImageScale.fromStr(imageJsonValue)
                ))

            emoteId = utils.getStrFromDict(emoteJson, 'id')
            emoteName = utils.getStrFromDict(emoteJson, 'name')
            emoteType = TwitchEmoteType.fromStr(utils.getStrFromDict(emoteJson, 'emote_type'))
            subscriberTier = TwitchSubscriberTier.fromStr(utils.getStrFromDict(emoteJson, 'tier'))

            emoteDetailsList.append(TwitchEmoteDetails(
                emoteImages = emoteImages,
                emoteId = emoteId,
                emoteName = emoteName,
                emoteType = emoteType,
                subscriberTier = subscriberTier
            ))

        return emoteDetailsList

    async def fetchLiveUserDetails(
        self,
        twitchAccessToken: str,
        userNames: List[str]
    ) -> List[TwitchLiveUserDetails]:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not utils.areValidStrs(userNames):
            raise ValueError(f'userNames argument is malformed: \"{userNames}\"')
        elif len(userNames) > 100:
            raise ValueError(f'userNames argument has too many values (len is {len(userNames)}, max is 100): \"{userNames}\"')

        userNames.sort(key = lambda userName: userName.lower())
        self.__timber.log('TwitchApiService', f'Fetching live user details... (userNames=\"{userNames}\")')

        userNamesStr = '&user_login='.join(userNames)
        twitchClientId = await self.__twitchCredentialsProvider.getTwitchClientId()
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = f'https://api.twitch.tv/helix/streams?first=100&user_login={userNamesStr}',
                headers = {
                    'Authorization': f'Bearer {twitchAccessToken}',
                    'Client-Id': twitchClientId
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching live user details (userNames=\"{userNames}\"): {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchApiService encountered network error when fetching when fetching user details (userNames=\"{userNames}\"): {e}')

        responseStatusCode = response.getStatusCode()
        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiService', f'Received a null/empty JSON response when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty JSON response when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')
        elif responseStatusCode == 401 or ('error' in jsonResponse and len(jsonResponse['error']) >= 1):
            self.__timber.log('TwitchApiService', f'Received an error ({responseStatusCode}) when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')
            raise TwitchTokenIsExpiredException(f'TwitchApiService received an error ({responseStatusCode}) when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')
        elif responseStatusCode != 200:
            self.__timber.log('TwitchApiService', f'Encountered non-200 HTTP status code when fetching live user details (userNames=\"{userNames}\"): {responseStatusCode}')
            raise GenericNetworkException(f'TwitchApiService encountered non-200 HTTP status code when fetching live user details (userNames=\"{userNames}\"): {responseStatusCode}')

        data: Optional[List[Dict[str, Any]]] = jsonResponse.get('data')
        users: List[TwitchLiveUserDetails] = list()

        if not utils.hasItems(data):
            return users

        for dataEntry in data:
            users.append(TwitchLiveUserDetails(
                isMature = utils.getBoolFromDict(dataEntry, 'is_mature', fallback = False),
                streamId = utils.getStrFromDict(dataEntry, 'id'),
                userId = utils.getStrFromDict(dataEntry, 'user_id'),
                userLogin = utils.getStrFromDict(dataEntry, 'user_login'),
                userName = utils.getStrFromDict(dataEntry, 'user_name'),
                viewerCount = utils.getIntFromDict(dataEntry, 'viewer_count', fallback = 0),
                gameId = utils.getStrFromDict(dataEntry, 'game_id', fallback = ''),
                gameName = utils.getStrFromDict(dataEntry, 'game_name', fallback = ''),
                language = utils.getStrFromDict(dataEntry, 'language', fallback = ''),
                thumbnailUrl = utils.getStrFromDict(dataEntry, 'thumbnail_url', fallback = ''),
                title = utils.getStrFromDict(dataEntry, 'title', fallback = ''),
                streamType = TwitchStreamType.fromStr(utils.getStrFromDict(dataEntry, 'type', fallback = ''))
            ))

        users.sort(key = lambda user: user.getUserName().lower())
        return users

    async def fetchTokens(self, code: str) -> TwitchTokensDetails:
        if not utils.isValidStr(code):
            raise ValueError(f'code argument is malformed: \"{code}\"')

        self.__timber.log('TwitchApiService', f'Fetching tokens... (code=\"{code}\")')

        twitchClientId = await self.__twitchCredentialsProvider.getTwitchClientId()
        twitchClientSecret = await self.__twitchCredentialsProvider.getTwitchClientSecret()
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.post(
                url = f'https://id.twitch.tv/oauth2/token?client_id={twitchClientId}&client_secret={twitchClientSecret}&code={code}&grant_type=authorization_code&redirect_uri=http://localhost'
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching tokens (code=\"{code}\"): {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchApiService encountered network error when fetching tokens (code=\"{code}\"): {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('TwitchApiService', f'Encountered non-200 HTTP status code when fetching tokens (code=\"{code}\"): {response.getStatusCode()}')
            raise GenericNetworkException(f'TwitchApiService encountered non-200 HTTP status code when fetching tokens (code=\"{code}\"): {response.getStatusCode()}')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiService', f'Received a null/empty JSON response when fetching tokens (code=\"{code}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty JSON response when fetching tokens (code=\"{code}\"): {jsonResponse}')
        elif 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('TwitchApiService', f'Received an error of some kind when fetching tokens (code=\"{code}\"): {jsonResponse}')
            raise TwitchErrorException(f'TwitchApiService received an error of some kind when fetching tokens (code=\"{code}\"): {jsonResponse}')

        expirationTime = await self.__calculateExpirationTime(
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in', fallback = -1)
        )

        accessToken = utils.getStrFromDict(jsonResponse, 'access_token', fallback = '')
        if not utils.isValidStr(accessToken):
            self.__timber.log('TwitchApiService', f'Received malformed \"access_token\" ({accessToken}) when fetching tokens (code=\"{code}\"): {jsonResponse}')
            raise TwitchAccessTokenMissingException(f'TwitchApiService received malformed \"access_token\" ({accessToken}) when fetching tokens (code=\"{code}\"): {jsonResponse}')

        refreshToken = utils.getStrFromDict(jsonResponse, 'refresh_token', fallback = '')
        if not utils.isValidStr(refreshToken):
            self.__timber.log('TwitchApiService', f'Received malformed \"refresh_token\" ({refreshToken}) when fetching tokens (code=\"{code}\"): {jsonResponse}')
            raise TwitchRefreshTokenMissingException(f'TwitchApiService received malformed \"refresh_token\" ({refreshToken}) when fetching tokens (code=\"{code}\"): {jsonResponse}')

        return TwitchTokensDetails(
            expirationTime = expirationTime,
            accessToken = accessToken,
            refreshToken = refreshToken
        )

    async def fetchUserDetails(
        self,
        twitchAccessToken: str,
        userName: str
    ) -> Optional[TwitchUserDetails]:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        userName = userName.lower()
        self.__timber.log('TwitchApiService', f'Fetching user details... (userName=\"{userName}\")')

        twitchClientId = await self.__twitchCredentialsProvider.getTwitchClientId()
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = f'https://api.twitch.tv/helix/users?login={userName}',
                headers = {
                    'Authorization': f'Bearer {twitchAccessToken}',
                    'Client-Id': twitchClientId
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching user details (userName=\"{userName}\"): {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchApiService encountered network error when fetching when fetching user details (userName=\"{userName}\"): {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('TwitchApiService', f'Encountered non-200 HTTP status code when fetching user details (userName=\"{userName}\"): {response.getStatusCode()}')
            raise GenericNetworkException(f'TwitchApiService encountered non-200 HTTP status code when fetching user details (userName=\"{userName}\"): {response.getStatusCode()}')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiService', f'Received a null/empty JSON response when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty JSON response when fetching user details (userName=\"{userName}\"): {jsonResponse}')
        elif 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('TwitchApiService', f'Received an error of some kind when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            raise TwitchErrorException(f'TwitchApiService received an error of some kind when fetching user details (userName=\"{userName}\"): {jsonResponse}')

        data: Optional[List[Dict[str, Any]]] = jsonResponse.get('data')

        if not utils.hasItems(data):
            self.__timber.log('TwitchApiService', f'Received a null/empty \"data\" field in JSON response when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            return None

        entry: Optional[Dict[str, Any]] = None

        for dataEntry in data:
            if utils.getStrFromDict(dataEntry, 'login').lower() == userName:
                entry = dataEntry
                break

        if entry is None:
            self.__timber.log('TwitchApiService', f'Couldn\'t find entry with matching \"login\" field in JSON response when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            return None

        return TwitchUserDetails(
            displayName = utils.getStrFromDict(entry, 'display_name'),
            login = utils.getStrFromDict(entry, 'login'),
            userId = utils.getStrFromDict(entry, 'id'),
            broadcasterType = TwitchBroadcasterType.fromStr(utils.getStrFromDict(entry, 'broadcaster_type')),
            userType = TwitchUserType.fromStr(utils.getStrFromDict(entry, 'type'))
        )

    async def fetchUserSubscriptionDetails(
        self,
        broadcasterId: str,
        twitchAccessToken: str,
        userId: str
    ) -> Optional[TwitchUserSubscriptionDetails]:
        if not utils.isValidStr(broadcasterId):
            raise ValueError(f'broadcasterId argument is malformed: \"{broadcasterId}\"')
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        self.__timber.log('TwitchApiService', f'Fetching user subscription details... (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\")')

        twitchClientId = await self.__twitchCredentialsProvider.getTwitchClientId()
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = f'https://api.twitch.tv/helix/subscriptions?broadcaster_id={broadcasterId}&user_id={userId}',
                headers = {
                    'Authorization': f'Bearer {twitchAccessToken}',
                    'Client-Id': twitchClientId
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchApiService encountered network error when fetching when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('TwitchApiService', f'Encountered non-200 HTTP status code when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {response.getStatusCode()}')
            raise GenericNetworkException(f'TwitchApiService encountered non-200 HTTP status code when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {response.getStatusCode()}')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiService', f'Received a null/empty JSON response when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty JSON response when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
        elif 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('TwitchApiService', f'Received an error of some kind when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
            raise TwitchErrorException(f'TwitchApiService received an error of some kind when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')

        data: Optional[List[Dict[str, Any]]] = jsonResponse.get('data')

        if not utils.hasItems(data):
            self.__timber.log('TwitchApiService', f'Received a null/empty \"data\" field in JSON response when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
            return None

        entry: Optional[Dict[str, Any]] = None

        for dataEntry in data:
            if dataEntry.get('user_id') == userId:
                entry = dataEntry
                break

        if entry is None:
            self.__timber.log('TwitchApiService', f'Couldn\'t find entry with matching \"user_id\" field in JSON response when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
            return None

        return TwitchUserSubscriptionDetails(
            isGift = utils.getBoolFromDict(entry, 'is_gift', fallback = False),
            userId = utils.getStrFromDict(entry, 'user_id'),
            userName = utils.getStrFromDict(entry, 'user_name'),
            subscriberTier = TwitchSubscriberTier.fromStr(utils.getStrFromDict(entry, 'tier'))
        )

    async def refreshTokens(self, twitchRefreshToken: str) -> TwitchTokensDetails:
        if not utils.isValidStr(twitchRefreshToken):
            raise ValueError(f'twitchRefreshToken argument is malformed: \"{twitchRefreshToken}\"')

        self.__timber.log('TwitchApiService', f'Refreshing tokens... (twitchRefreshToken=\"{twitchRefreshToken}\")')

        twitchClientId = await self.__twitchCredentialsProvider.getTwitchClientId()
        twitchClientSecret = await self.__twitchCredentialsProvider.getTwitchClientSecret()
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.post(
                url = 'https://id.twitch.tv/oauth2/token',
                json = {
                    'client_id': twitchClientId,
                    'client_secret': twitchClientSecret,
                    'grant_type': 'refresh_token',
                    'refresh_token': twitchRefreshToken
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchApiService', f'Encountered network error when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchApiService encountered network error when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {e}')

        if response.getStatusCode() == 400:
            self.__timber.log('TwitchApiService', f'Encountered HTTP 400 status code when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {response.getStatusCode()}')
            raise TwitchPasswordChangedException(f'Encountered HTTP 400 status code when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {response.getStatusCode()}')
        elif response.getStatusCode() != 200:
            self.__timber.log('TwitchApiService', f'Encountered non-200 HTTP status code when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {response.getStatusCode()}')
            raise GenericNetworkException(f'TwitchApiService encountered non-200 HTTP status code when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {response.getStatusCode()}')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiService', f'Received a null/empty JSON response when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty JSON response when fetching user subscription details (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
        elif 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('TwitchApiService', f'Received an error of some kind when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchErrorException(f'TwitchApiService received an error of some kind when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        expirationTime = await self.__calculateExpirationTime(
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in', fallback = -1)
        )

        accessToken = utils.getStrFromDict(jsonResponse, 'access_token', fallback = '')
        if not utils.isValidStr(accessToken):
            self.__timber.log('TwitchApiService', f'Received malformed \"access_token\" ({accessToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchAccessTokenMissingException(f'TwitchApiService received malformed \"access_token\" ({accessToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        refreshToken = utils.getStrFromDict(jsonResponse, 'refresh_token', fallback = '')
        if not utils.isValidStr(refreshToken):
            self.__timber.log('TwitchApiService', f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchRefreshTokenMissingException(f'TwitchApiService received malformed \"refresh_token\" ({refreshToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        return TwitchTokensDetails(
            expirationTime = expirationTime,
            accessToken = accessToken,
            refreshToken = refreshToken
        )

    async def validateTokens(self, twitchAccessToken: str) -> Optional[datetime]:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        self.__timber.log('TwitchApiService', f'Validating tokens... (twitchAccessToken=\"{twitchAccessToken}\")')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = 'https://id.twitch.tv/oauth2/validate',
                headers = {
                    'Authorization': f'OAuth {twitchAccessToken}'
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchApiService', f'Encountered network error when refreshing tokens (twitchAccessToken=\"{twitchAccessToken}\"): {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchApiService encountered network error when refreshing tokens (twitchAccessToken=\"{twitchAccessToken}\"): {e}')

        responseStatusCode = response.getStatusCode()
        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        clientId: Optional[str] = None
        if jsonResponse is not None and utils.isValidStr(jsonResponse.get('client_id')):
            clientId = utils.getStrFromDict(jsonResponse, 'client_id')

        expiresInSeconds: Optional[int] = None
        if jsonResponse is not None and utils.isValidInt(jsonResponse.get('expires_in')):
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in')

        if responseStatusCode != 200 or not utils.isValidStr(clientId) or not utils.isValidInt(expiresInSeconds):
            return None

        nowDateTime = datetime.now(self.__timeZone)
        expiresInTimeDelta = timedelta(seconds = expiresInSeconds)
        expirationTime = nowDateTime + expiresInTimeDelta

        return expirationTime
