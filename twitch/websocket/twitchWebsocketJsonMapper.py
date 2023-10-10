import json
import traceback
from json.decoder import JSONDecodeError
from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
    from CynanBotCommon.twitch.websocket.websocketMessageType import \
        WebsocketMessageType
    from CynanBotCommon.twitch.websocket.websocketMetadata import \
        WebsocketMetadata
    from CynanBotCommon.twitch.websocket.websocketPayload import \
        WebsocketPayload
    from CynanBotCommon.twitch.websocket.websocketSession import \
        WebsocketSession
    from CynanBotCommon.twitch.websocket.websocketSubscription import \
        WebsocketSubscription
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
except:
    import utils
    from simpleDateTime import SimpleDateTime
    from timber.timberInterface import TimberInterface

    from twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle
    from twitch.websocket.websocketMessageType import WebsocketMessageType
    from twitch.websocket.websocketMetadata import WebsocketMetadata
    from twitch.websocket.websocketPayload import WebsocketPayload
    from twitch.websocket.websocketSession import WebsocketSession
    from twitch.websocket.websocketSubscription import WebsocketSubscription
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType


class TwitchWebsocketJsonMapper(TwitchWebsocketJsonMapperInterface):

    def __init__(self, timber: TimberInterface):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: TimberInterface = timber

    async def __parseMetadata(self, metadataJson: Optional[Dict[str, Any]]) -> Optional[WebsocketMetadata]:
        if not isinstance(metadataJson, Dict) or not utils.hasItems(metadataJson):
            return None

        messageTimestamp = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(metadataJson, 'message_timestamp')))
        messageId = utils.getStrFromDict(metadataJson, 'message_id')
        messageType = WebsocketMessageType.fromStr(utils.getStrFromDict(metadataJson, 'message_type'))
        subscriptionType = WebsocketSubscriptionType.fromStr(utils.getStrFromDict(metadataJson, 'subscription_type', fallback = ''))
        subscriptionVersion: Optional[str] = None

        if utils.isValidStr(metadataJson.get('subscription_version')):
            subscriptionVersion = utils.getStrFromDict(metadataJson, 'subscription_version')

        return WebsocketMetadata(
            messageTimestamp = messageTimestamp,
            messageId = messageId,
            subscriptionVersion = subscriptionVersion,
            messageType = messageType,
            subscriptionType = subscriptionType
        )

    async def __parsePayload(self, payloadJson: Optional[Dict[str, Any]]) -> Optional[WebsocketPayload]:
        if not isinstance(payloadJson, Dict) or not utils.hasItems(payloadJson):
            return None

        session = await self.__parseSession(payloadJson.get('session'))
        subscription = await self.__parseSubscription(payloadJson.get('subscription'))

        return WebsocketPayload(
            session = session,
            subscription  = subscription
        )

    async def __parseSession(self, sessionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketSession]:
        if not isinstance(sessionJson, Dict) or not utils.hasItems(sessionJson):
            return None

        # TODO

        return None

    async def __parseSubscription(self, subscriptionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketSubscription]:
        if not isinstance(subscriptionJson, Dict) or not utils.hasItems(subscriptionJson):
            return None

        # TODO

        return None

    async def toWebsocketDataBundle(self, message: Optional[str]) -> Optional[WebsocketDataBundle]:
        if not utils.isValidStr(message):
            return None

        messageJson: Optional[Dict[str, Any]] = None
        exception: Optional[JSONDecodeError] = None

        try:
            json.loads(message)
        except JSONDecodeError as e:
            exception = e

        if exception is not None:
            self.__timber.log('TwitchWebsocketJsonMapper', f'Exception occurred when attempting to parse Websocket into a viable dictionary (message=\"{message}\") (exception=\"{exception}\")', exception, traceback.format_exc())
            return None
        elif not utils.hasItems(messageJson):
            self.__timber.log('TwitchWebsocketJsonMapper', f'Failed to parse Websocket message into a viable dictionary (message=\"{message}\")')
            return None

        metadata = await self.__parseMetadata(messageJson.get('metadata'))
        payload = await self.__parsePayload(messageJson.get('payload'))

        if metadata is None or payload is None:
            self.__timber.log('TwitchWebsocketJsonMapper', f'Websocket message ({message}) is missing either \"metadata\" ({metadata}) or \"payload\" ({payload})')
            return None

        return WebsocketDataBundle(
            metadata = metadata,
            payload = payload
        )
