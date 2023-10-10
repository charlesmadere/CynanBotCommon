import json
import traceback
from json.decoder import JSONDecodeError
from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.twitchSubscriberTier import TwitchSubscriberTier
    from CynanBotCommon.twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from CynanBotCommon.twitch.websocket.websocketCondition import \
        WebsocketCondition
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
    from CynanBotCommon.twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
except:
    import utils
    from simpleDateTime import SimpleDateTime
    from timber.timberInterface import TimberInterface

    from twitch.twitchSubscriberTier import TwitchSubscriberTier
    from twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle
    from twitch.websocket.websocketMessageType import WebsocketMessageType
    from twitch.websocket.websocketMetadata import WebsocketMetadata
    from twitch.websocket.websocketPayload import WebsocketPayload
    from twitch.websocket.websocketSession import WebsocketSession
    from twitch.websocket.websocketSubscription import WebsocketSubscription
    from twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType


class TwitchWebsocketJsonMapper(TwitchWebsocketJsonMapperInterface):

    def __init__(self, timber: TimberInterface):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: TimberInterface = timber

    async def __parseCondition(self, conditionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketCondition]:
        if not isinstance(conditionJson, Dict):
            return None

        isAnonymous: Optional[bool] = None
        if 'is_anonymous' in conditionJson:
            isAnonymous = utils.getBoolFromDict(conditionJson, 'is_anonymous')

        isGift: Optional[bool] = None
        if 'is_gift' in conditionJson:
            isGift = utils.getBoolFromDict(conditionJson, 'is_gift')

        isPermanent: Optional[bool] = None
        if 'is_permanent' in conditionJson:
            isPermanent = utils.getBoolFromDict(conditionJson, 'is_permanent')

        bits: Optional[int] = None
        if 'bits' in conditionJson:
            bits = utils.getIntFromDict(conditionJson, 'bits')

        viewers: Optional[int] = None
        if 'viewers' in conditionJson:
            viewers = utils.getIntFromDict(conditionJson, 'viewers')

        broadcasterUserId: Optional[str] = None
        if 'broadcaster_user_id' in conditionJson:
            broadcasterUserId = utils.getStrFromDict(conditionJson, 'broadcaster_user_id')

        broadcasterUserLogin: Optional[str] = None
        if 'broadcaster_user_login' in conditionJson:
            broadcasterUserLogin = utils.getStrFromDict(conditionJson, 'broadcaster_user_login')

        broadcasterUserName: Optional[str] = None
        if 'broadcaster_user_name' in conditionJson:
            broadcasterUserName = utils.getStrFromDict(conditionJson, 'broadcaster_user_name')

        categoryId: Optional[str] = None
        if 'category_id' in conditionJson:
            categoryId = utils.getStrFromDict(conditionJson, 'category_id')

        categoryName: Optional[str] = None
        if 'category_name' in conditionJson:
            categoryName = utils.getStrFromDict(conditionJson, 'category_name')

        clientId: Optional[str] = None
        if 'client_id' in conditionJson:
            clientId = utils.getStrFromDict(conditionJson, 'client_id')

        fromBroadcasterUserId: Optional[str] = None
        if 'from_broadcaster_user_id' in conditionJson:
            fromBroadcasterUserId = utils.getStrFromDict(conditionJson, 'from_broadcaster_user_id')

        fromBroadcasterUserLogin: Optional[str] = None
        if 'from_broadcaster_user_login' in conditionJson:
            fromBroadcasterUserLogin = utils.getStrFromDict(conditionJson, 'from_broadcaster_user_login')

        fromBroadcasterUserName: Optional[str] = None
        if 'from_broadcaster_user_name' in conditionJson:
            fromBroadcasterUserName = utils.getStrFromDict(conditionJson, 'from_broadcaster_user_name')

        message: Optional[str] = None
        if 'message' in conditionJson:
            message = utils.getStrFromDict(conditionJson, 'message')

        moderatorUserId: Optional[str] = None
        if 'moderator_user_id' in conditionJson:
            moderatorUserId = utils.getStrFromDict(conditionJson, 'moderator_user_id')

        moderatorUserLogin: Optional[str] = None
        if 'moderator_user_login' in conditionJson:
            moderatorUserLogin = utils.getStrFromDict(conditionJson, 'moderator_user_login')

        moderatorUserName: Optional[str] = None
        if 'moderator_user_name' in conditionJson:
            moderatorUserName = utils.getStrFromDict(conditionJson, 'moderator_user_name')

        reason: Optional[str] = None
        if 'reason' in conditionJson:
            reason = utils.getStrFromDict(conditionJson, 'reason')

        rewardId: Optional[str] = None
        if 'reward_id' in conditionJson:
            rewardId = utils.getStrFromDict(conditionJson, 'reward_id')

        title: Optional[str] = None
        if 'title' in conditionJson:
            title = utils.getStrFromDict(conditionJson, 'title')

        toBroadcasterUserId: Optional[str] = None
        if 'to_broadcaster_user_id' in conditionJson:
            toBroadcasterUserId = utils.getStrFromDict(conditionJson, 'to_broadcaster_user_id')

        toBroadcasterUserLogin: Optional[str] = None
        if 'to_broadcaster_user_login' in conditionJson:
            toBroadcasterUserLogin = utils.getStrFromDict(conditionJson, 'to_broadcaster_user_login')

        toBroadcasterUserName: Optional[str] = None
        if 'to_broadcaster_user_name' in conditionJson:
            toBroadcasterUserName = utils.getStrFromDict(conditionJson, 'to_broadcaster_user_name')

        userId: Optional[str] = None
        if 'user_id' in conditionJson:
            userId = utils.getStrFromDict(conditionJson, 'user_id')

        userLogin: Optional[str] = None
        if 'user_login' in conditionJson:
            userLogin = utils.getStrFromDict(conditionJson, 'user_login')

        userName: Optional[str] = None
        if 'user_name' in conditionJson:
            userName = utils.getStrFromDict(conditionJson, 'user_name')

        tier: Optional[TwitchSubscriberTier] = None
        if 'tier' in conditionJson:
            tier = TwitchSubscriberTier.fromStr(utils.getStrFromDict(conditionJson, 'tier'))

        return WebsocketCondition(
            isAnonymous = isAnonymous,
            isGift = isGift,
            isPermanent = isPermanent,
            bits = bits,
            viewers = viewers,
            broadcasterUserId = broadcasterUserId,
            broadcasterUserLogin = broadcasterUserLogin,
            broadcasterUserName = broadcasterUserName,
            categoryId = categoryId,
            categoryName = categoryName,
            clientId = clientId,
            fromBroadcasterUserId = fromBroadcasterUserId,
            fromBroadcasterUserLogin = fromBroadcasterUserLogin,
            fromBroadcasterUserName = fromBroadcasterUserName,
            message = message,
            moderatorUserId = moderatorUserId,
            moderatorUserLogin = moderatorUserLogin,
            moderatorUserName = moderatorUserName,
            reason = reason,
            rewardId = rewardId,
            title = title,
            toBroadcasterUserId = toBroadcasterUserId,
            toBroadcasterUserLogin = toBroadcasterUserLogin,
            toBroadcasterUserName = toBroadcasterUserName,
            userId = userId,
            userLogin = userLogin,
            userName = userName,
            tier = tier
        )

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

        cost = utils.getIntFromDict(subscriptionJson, 'cost')
        createdAt = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(subscriptionJson, 'created_at')))
        subscriptionId = utils.getStrFromDict(subscriptionJson, 'id')
        version = utils.getStrFromDict(subscriptionJson, 'version')
        condition = await self.__parseCondition(subscriptionJson.get('condition'))
        status = WebsocketSubscriptionStatus.fromStr(utils.getStrFromDict(subscriptionJson, 'status'))
        subscriptionType = WebsocketSubscriptionType.fromStr(utils.getStrFromDict(subscriptionJson, 'type'))

        return WebsocketSubscription(
            cost = cost,
            createdAt = createdAt,
            subscriptionId = subscriptionId,
            version = version,
            condition = condition,
            status = status,
            subscriptionType = subscriptionType
        )

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
