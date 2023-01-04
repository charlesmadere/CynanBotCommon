from typing import Any, Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.twitch.exceptions import (
        TwitchAccessTokenMissingException, TwitchErrorException,
        TwitchJsonException, TwitchRefreshTokenMissingException,
        TwitchTokenIsExpiredException)
    from CynanBotCommon.twitch.twitchBroadcasterType import \
        TwitchBroadcasterType
    from CynanBotCommon.twitch.twitchCredentialsProviderInterface import \
        TwitchCredentialsProviderInterface
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
    from timber.timber import Timber
    from twitch.exceptions import (TwitchAccessTokenMissingException,
                                   TwitchErrorException, TwitchJsonException,
                                   TwitchRefreshTokenMissingException,
                                   TwitchTokenIsExpiredException)
    from twitch.twitchBroadcasterType import TwitchBroadcasterType
    from twitch.twitchCredentialsProviderInterface import \
        TwitchCredentialsProviderInterface
    from twitch.twitchLiveUserDetails import TwitchLiveUserDetails
    from twitch.twitchStreamType import TwitchStreamType
    from twitch.twitchSubscriberTier import TwitchSubscriberTier
    from twitch.twitchTokensDetails import TwitchTokensDetails
    from twitch.twitchUserDetails import TwitchUserDetails
    from twitch.twitchUserSubscriptionDetails import \
        TwitchUserSubscriptionDetails
    from twitch.twitchUserType import TwitchUserType


class TwitchApiService():

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: Timber,
        twitchCredentialsProviderInterface: TwitchCredentialsProviderInterface
    ):
        if not isinstance(networkClientProvider, NetworkClientProvider):
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchCredentialsProviderInterface, TwitchCredentialsProviderInterface):
            raise ValueError(f'twitchCredentialsProviderInterface argument is malformed: \"{twitchCredentialsProviderInterface}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber
        self.__twitchCredentialsProviderInterface: TwitchCredentialsProviderInterface = twitchCredentialsProviderInterface

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

        self.__timber.log('TwitchApiService', f'Fetching live user details... (userNames=\"{userNames}\")')

        userNamesStr = '&user_login='.join(userNames)
        twitchClientId = await self.__twitchCredentialsProviderInterface.getTwitchClientId()
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
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching live user details (userNames=\"{userNames}\"): {e}', e)
            raise GenericNetworkException(f'TwitchApiService encountered network error when fetching when fetching user details (userNames=\"{userNames}\"): {e}')

        responseStatusCode = response.getStatusCode()
        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiService', f'Received a null/empty JSON response when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiService received a null/empty JSON response when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')

        if responseStatusCode == 401 or ('error' in jsonResponse and len(jsonResponse['error']) >= 1):
            self.__timber.log('TwitchApiService', f'Received an error ({responseStatusCode}) when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')
            raise TwitchTokenIsExpiredException(f'TwitchApiService received an error ({responseStatusCode}) when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')

        data: Optional[List[Dict[str, Any]]] = jsonResponse.get('data')
        users: List[TwitchLiveUserDetails] = list()

        if not utils.hasItems(data):
            self.__timber.log('TwitchApiService', f'Received null/empty \"data\" field in JSON response when fetching live user details (userNames=\"{userNames}\"): {jsonResponse}')
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

    async def fetchUserDetails(
        self,
        twitchAccessToken: str,
        userName: str
    ) -> Optional[TwitchUserDetails]:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__timber.log('TwitchApiService', f'Fetching user details... (userName=\"{userName}\")')

        twitchClientId = await self.__twitchCredentialsProviderInterface.getTwitchClientId()
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
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching user details (userName=\"{userName}\"): {e}', e)
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
            if dataEntry.get('login') == userName:
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

        twitchClientId = await self.__twitchCredentialsProviderInterface.getTwitchClientId()
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
            self.__timber.log('TwitchApiService', f'Encountered network error when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {e}', e)
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

        twitchClientId = await self.__twitchCredentialsProviderInterface.getTwitchClientId()
        twitchClientSecret = await self.__twitchCredentialsProviderInterface.getTwitchClientSecret()
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
            self.__timber.log('TwitchApiService', f'Encountered network error when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {e}', e)
            raise GenericNetworkException(f'TwitchApiService encountered network error when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {e}')

        if response.getStatusCode() != 200:
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

        accessToken = utils.getStrFromDict(jsonResponse, 'access_token', fallback = '')
        if not utils.isValidStr(accessToken):
            self.__timber.log('TwitchApiService', f'Received malformed \"access_token\" ({accessToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchAccessTokenMissingException(f'TwitchApiService received malformed \"access_token\" ({accessToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        refreshToken = utils.getStrFromDict(jsonResponse, 'refresh_token', fallback = '')
        if not utils.isValidStr(refreshToken):
            self.__timber.log('TwitchApiService', f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchRefreshTokenMissingException(f'TwitchApiService received malformed \"refresh_token\" ({refreshToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        return TwitchTokensDetails(
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in', fallback = -1),
            accessToken = accessToken,
            refreshToken = refreshToken
        )

    async def validateTokens(self, twitchAccessToken: str) -> Optional[int]:
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
            self.__timber.log('TwitchApiService', f'Encountered network error when refreshing tokens (twitchAccessToken=\"{twitchAccessToken}\"): {e}', e)
            raise GenericNetworkException(f'TwitchApiService encountered network error when refreshing tokens (twitchAccessToken=\"{twitchAccessToken}\"): {e}')

        responseStatusCode = response.getStatusCode()
        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        clientId: Optional[str] = None
        if jsonResponse is not None and utils.isValidStr(jsonResponse.get('client_id')):
            clientId = utils.getStrFromDict(jsonResponse, 'client_id')

        expiresInSeconds: int = -1
        if jsonResponse is not None and utils.isValidInt(jsonResponse.get('expires_in')):
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in')

        if responseStatusCode == 200 and utils.isValidStr(clientId) and utils.isValidInt(expiresInSeconds):
            return expiresInSeconds
        else:
            return None
