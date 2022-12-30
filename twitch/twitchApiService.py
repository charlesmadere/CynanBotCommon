from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.twitch.exceptions import (
        TwitchAccessTokenMissingException, TwitchErrorException,
        TwitchJsonException, TwitchRefreshTokenMissingException)
    from CynanBotCommon.twitch.twitchBroadcasterType import \
        TwitchBroadcasterType
    from CynanBotCommon.twitch.twitchCredentialsProviderInterface import \
        TwitchCredentialsProviderInterface
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
                                   TwitchRefreshTokenMissingException)
    from twitch.twitchBroadcasterType import TwitchBroadcasterType
    from twitch.twitchCredentialsProviderInterface import \
        TwitchCredentialsProviderInterface
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

    async def fetchUserDetails(
        self,
        twitchAccessToken: str,
        userName: str
    ) -> TwitchUserDetails:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__timber.log('TwitchApiRepository', f'Fetching user details... (userName=\"{userName}\")')

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
            self.__timber.log('TwitchApiRepository', f'Encountered network error when fetching user details (userName=\"{userName}\"): {e}', e)
            raise GenericNetworkException(f'Encountered network error when fetching when fetching user details (userName=\"{userName}\"): {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('TwitchApiRepository', f'Encountered non-200 HTTP status code when fetching user details (userName=\"{userName}\"): {response.getStatusCode()}')
            raise GenericNetworkException(f'Encountered non-200 HTTP status code when fetching user details (userName=\"{userName}\"): {response.getStatusCode()}')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiRepository', f'Received a null/empty JSON response when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiRepository received a null/empty JSON response when fetching user details (userName=\"{userName}\"): {jsonResponse}')
        elif 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('TwitchApiRepository', f'Received an error of some kind when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            raise TwitchErrorException(f'TwitchApiRepository received an error of some kind when fetching user details (userName=\"{userName}\"): {jsonResponse}')

        data: Optional[Dict[str, Any]] = jsonResponse.get('data')

        if not utils.hasItems(data):
            self.__timber.log('TwitchApiRepository', f'Received JSON response with null/empty \"data\" field when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiRepository received JSON response with null/empty \"data\" field when fetching user details (userName=\"{userName}\"): {jsonResponse}')

        entry: Optional[Dict[str, Any]] = None

        for dataEntry in data:
            if dataEntry.get('login') == userName:
                entry = dataEntry
                break

        if entry is None:
            self.__timber.log('TwitchApiRepository', f'Couldn\'t find data entry with corresponding \"login\" field when fetching user details (userName=\"{userName}\"): {jsonResponse}')
            raise RuntimeError(f'TwitchApiRepository couldn\'t find data entry with corresponding \"login\" field when fetching user details (userName=\"{userName}\"): {jsonResponse}')

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

        self.__timber.log('TwitchApiRepository', f'Fetching user subscription details... (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\")')

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
            self.__timber.log('TwitchApiRepository', f'Encountered network error when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {e}', e)
            raise GenericNetworkException(f'Encountered network error when fetching when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('TwitchApiRepository', f'Encountered non-200 HTTP status code when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {response.getStatusCode()}')
            raise GenericNetworkException(f'Encountered non-200 HTTP status code when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {response.getStatusCode()}')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiRepository', f'Received a null/empty JSON response when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiRepository received a null/empty JSON response when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
        elif 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('TwitchApiRepository', f'Received an error of some kind when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')
            raise TwitchErrorException(f'TwitchApiRepository received an error of some kind when fetching user subscription details (broadcasterId=\"{broadcasterId}\") (userId=\"{userId}\"): {jsonResponse}')

        data: Optional[Dict[str, Any]] = jsonResponse.get('data')
        if not utils.hasItems(data):
            return None

        entry: Optional[Dict[str, Any]] = None

        for dataEntry in data:
            if dataEntry.get('user_id') == userId:
                entry = dataEntry
                break

        if entry is None:
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
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {e}', e)
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('TwitchTokensRepository', f'Encountered non-200 HTTP status code when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {response.getStatusCode()}')
            raise GenericNetworkException(f'TwitchTokensRepository encountered non-200 HTTP status code when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {response.getStatusCode()}')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchApiRepository', f'Received a null/empty JSON response when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchJsonException(f'TwitchApiRepository received a null/empty JSON response when fetching user subscription details (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
        elif 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('TwitchApiRepository', f'Received an error of some kind when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchErrorException(f'TwitchApiRepository received an error of some kind when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        accessToken = utils.getStrFromDict(jsonResponse, 'access_token', fallback = '')
        if not utils.isValidStr(accessToken):
            self.__timber.log('TwitchApiRepository', f'Received malformed \"access_token\" ({accessToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchAccessTokenMissingException(f'TwitchApiRepository received malformed \"access_token\" ({accessToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        refreshToken = utils.getStrFromDict(jsonResponse, 'refresh_token', fallback = '')
        if not utils.isValidStr(refreshToken):
            self.__timber.log('TwitchApiRepository', f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')
            raise TwitchRefreshTokenMissingException(f'TwitchApiRepository received malformed \"refresh_token\" ({refreshToken}) when refreshing tokens (twitchRefreshToken=\"{twitchRefreshToken}\"): {jsonResponse}')

        return TwitchTokensDetails(
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in', fallback = -1),
            accessToken = accessToken,
            refreshToken = refreshToken
        )

    async def validateTokens(self, twitchAccessToken: str) -> Optional[int]:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.post(
                url = 'https://id.twitch.tv/oauth2/validate',
                headers = {
                    'Authorization': f'OAuth {twitchAccessToken}'
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when refreshing tokens (twitchAccessToken=\"{twitchAccessToken}\"): {e}', e)
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when refreshing tokens (twitchAccessToken=\"{twitchAccessToken}\"): {e}')

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
