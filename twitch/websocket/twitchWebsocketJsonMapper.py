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
    from CynanBotCommon.twitch.websocket.websocketConnectionStatus import \
        WebsocketConnectionStatus
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
    from CynanBotCommon.twitch.websocket.websocketEvent import WebsocketEvent
    from CynanBotCommon.twitch.websocket.websocketMessageType import \
        WebsocketMessageType
    from CynanBotCommon.twitch.websocket.websocketMetadata import \
        WebsocketMetadata
    from CynanBotCommon.twitch.websocket.websocketPayload import \
        WebsocketPayload
    from CynanBotCommon.twitch.websocket.websocketReward import WebsocketReward
    from CynanBotCommon.twitch.websocket.websocketSession import \
        WebsocketSession
    from CynanBotCommon.twitch.websocket.websocketSubscription import \
        WebsocketSubscription
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from CynanBotCommon.twitch.websocket.websocketTransport import \
        WebsocketTransport
    from CynanBotCommon.twitch.websocket.websocketTransportMethod import \
        WebsocketTransportMethod
except:
    import utils
    from simpleDateTime import SimpleDateTime
    from timber.timberInterface import TimberInterface

    from twitch.twitchSubscriberTier import TwitchSubscriberTier
    from twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketConnectionStatus import \
        WebsocketConnectionStatus
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle
    from twitch.websocket.websocketEvent import WebsocketEvent
    from twitch.websocket.websocketMessageType import WebsocketMessageType
    from twitch.websocket.websocketMetadata import WebsocketMetadata
    from twitch.websocket.websocketPayload import WebsocketPayload
    from twitch.websocket.websocketReward import WebsocketReward
    from twitch.websocket.websocketSession import WebsocketSession
    from twitch.websocket.websocketSubscription import WebsocketSubscription
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from twitch.websocket.websocketTransport import WebsocketTransport
    from twitch.websocket.websocketTransportMethod import \
        WebsocketTransportMethod


class TwitchWebsocketJsonMapper(TwitchWebsocketJsonMapperInterface):

    def __init__(self, timber: TimberInterface):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: TimberInterface = timber

    async def parseWebsocketCondition(self, conditionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketCondition]:
        if not isinstance(conditionJson, Dict):
            return None

        isAnonymous: Optional[bool] = None
        if 'is_anonymous' in conditionJson and conditionJson.get('is_anonymous') is not None:
            isAnonymous = utils.getBoolFromDict(conditionJson, 'is_anonymous')

        isGift: Optional[bool] = None
        if 'is_gift' in conditionJson and conditionJson.get('is_gift') is not None:
            isGift = utils.getBoolFromDict(conditionJson, 'is_gift')

        isPermanent: Optional[bool] = None
        if 'is_permanent' in conditionJson and conditionJson.get('is_permanent') is not None:
            isPermanent = utils.getBoolFromDict(conditionJson, 'is_permanent')

        bits: Optional[int] = None
        if 'bits' in conditionJson and utils.isValidInt(conditionJson.get('bits')):
            bits = utils.getIntFromDict(conditionJson, 'bits')

        cumulativeTotal: Optional[int] = None
        if 'cumulative_total' in conditionJson and utils.isValidInt(conditionJson.get('cumulative_total')):
            cumulativeTotal = utils.getIntFromDict(conditionJson, 'cumulative_total')

        total: Optional[int] = None
        if 'total' in conditionJson and utils.isValidInt(conditionJson.get('total')):
            total = utils.getIntFromDict(conditionJson, 'total')

        viewers: Optional[int] = None
        if 'viewers' in conditionJson and utils.isValidInt(conditionJson.get('viewers')):
            viewers = utils.getIntFromDict(conditionJson, 'viewers')

        broadcasterUserId: Optional[str] = None
        if 'broadcaster_user_id' in conditionJson and utils.isValidStr(conditionJson.get('broadcaster_user_id')):
            broadcasterUserId = utils.getStrFromDict(conditionJson, 'broadcaster_user_id')

        broadcasterUserLogin: Optional[str] = None
        if 'broadcaster_user_login' in conditionJson and utils.isValidStr(conditionJson.get('broadcaster_user_login')):
            broadcasterUserLogin = utils.getStrFromDict(conditionJson, 'broadcaster_user_login')

        broadcasterUserName: Optional[str] = None
        if 'broadcaster_user_name' in conditionJson and utils.isValidStr(conditionJson.get('broadcaster_user_name')):
            broadcasterUserName = utils.getStrFromDict(conditionJson, 'broadcaster_user_name')

        categoryId: Optional[str] = None
        if 'category_id' in conditionJson and utils.isValidStr(conditionJson.get('category_id')):
            categoryId = utils.getStrFromDict(conditionJson, 'category_id')

        categoryName: Optional[str] = None
        if 'category_name' in conditionJson and utils.isValidStr(conditionJson.get('category_name')):
            categoryName = utils.getStrFromDict(conditionJson, 'category_name')

        clientId: Optional[str] = None
        if 'client_id' in conditionJson and utils.isValidStr(conditionJson.get('client_id')):
            clientId = utils.getStrFromDict(conditionJson, 'client_id')

        fromBroadcasterUserId: Optional[str] = None
        if 'from_broadcaster_user_id' in conditionJson and utils.isValidStr(conditionJson.get('from_broadcaster_user_id')):
            fromBroadcasterUserId = utils.getStrFromDict(conditionJson, 'from_broadcaster_user_id')

        fromBroadcasterUserLogin: Optional[str] = None
        if 'from_broadcaster_user_login' in conditionJson and utils.isValidStr(conditionJson.get('from_broadcaster_user_login')):
            fromBroadcasterUserLogin = utils.getStrFromDict(conditionJson, 'from_broadcaster_user_login')

        fromBroadcasterUserName: Optional[str] = None
        if 'from_broadcaster_user_name' in conditionJson and utils.isValidStr(conditionJson.get('from_broadcaster_user_name')):
            fromBroadcasterUserName = utils.getStrFromDict(conditionJson, 'from_broadcaster_user_name')

        message: Optional[str] = None
        if 'message' in conditionJson and utils.isValidStr(conditionJson.get('message')):
            message = utils.getStrFromDict(conditionJson, 'message')

        moderatorUserId: Optional[str] = None
        if 'moderator_user_id' in conditionJson and utils.isValidStr(conditionJson.get('moderator_user_id')):
            moderatorUserId = utils.getStrFromDict(conditionJson, 'moderator_user_id')

        moderatorUserLogin: Optional[str] = None
        if 'moderator_user_login' in conditionJson and utils.isValidStr(conditionJson.get('moderator_user_login')):
            moderatorUserLogin = utils.getStrFromDict(conditionJson, 'moderator_user_login')

        moderatorUserName: Optional[str] = None
        if 'moderator_user_name' in conditionJson and utils.isValidStr(conditionJson.get('moderator_user_name')):
            moderatorUserName = utils.getStrFromDict(conditionJson, 'moderator_user_name')

        reason: Optional[str] = None
        if 'reason' in conditionJson and utils.isValidBool(conditionJson.get('reason')):
            reason = utils.getStrFromDict(conditionJson, 'reason')

        rewardId: Optional[str] = None
        if 'reward_id' in conditionJson and utils.isValidStr(conditionJson.get('reward_id')):
            rewardId = utils.getStrFromDict(conditionJson, 'reward_id')

        title: Optional[str] = None
        if 'title' in conditionJson and utils.isValidStr(conditionJson.get('title')):
            title = utils.getStrFromDict(conditionJson, 'title')

        toBroadcasterUserId: Optional[str] = None
        if 'to_broadcaster_user_id' in conditionJson and utils.isValidStr(conditionJson.get('to_broadcaster_user_id')):
            toBroadcasterUserId = utils.getStrFromDict(conditionJson, 'to_broadcaster_user_id')

        toBroadcasterUserLogin: Optional[str] = None
        if 'to_broadcaster_user_login' in conditionJson and utils.isValidStr(conditionJson.get('to_broadcaster_user_login')):
            toBroadcasterUserLogin = utils.getStrFromDict(conditionJson, 'to_broadcaster_user_login')

        toBroadcasterUserName: Optional[str] = None
        if 'to_broadcaster_user_name' in conditionJson and utils.isValidStr(conditionJson.get('to_broadcaster_user_name')):
            toBroadcasterUserName = utils.getStrFromDict(conditionJson, 'to_broadcaster_user_name')

        userId: Optional[str] = None
        if 'user_id' in conditionJson and utils.isValidStr(conditionJson.get('user_id')):
            userId = utils.getStrFromDict(conditionJson, 'user_id')

        userInput: Optional[str] = None
        if 'user_input' in conditionJson and utils.isValidStr(conditionJson.get('user_input')):
            userInput = utils.getStrFromDict(conditionJson, 'user_input')

        userLogin: Optional[str] = None
        if 'user_login' in conditionJson and utils.isValidStr(conditionJson.get('user_login')):
            userLogin = utils.getStrFromDict(conditionJson, 'user_login')

        userName: Optional[str] = None
        if 'user_name' in conditionJson and utils.isValidStr(conditionJson.get('user_name')):
            userName = utils.getStrFromDict(conditionJson, 'user_name')

        tier: Optional[TwitchSubscriberTier] = None
        if 'tier' in conditionJson and utils.isValidStr(conditionJson.get('tier')):
            tier = TwitchSubscriberTier.fromStr(utils.getStrFromDict(conditionJson, 'tier'))

        reward: Optional[WebsocketReward] = None
        if 'reward' in conditionJson:
            reward = await self.parseWebsocketReward(conditionJson.get('reward'))

        return WebsocketCondition(
            isAnonymous = isAnonymous,
            isGift = isGift,
            isPermanent = isPermanent,
            bits = bits,
            cumulativeTotal = cumulativeTotal,
            total = total,
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
            userInput = userInput,
            userLogin = userLogin,
            userName = userName,
            tier = tier,
            reward = reward
        )

    async def __parseMetadata(self, metadataJson: Optional[Dict[str, Any]]) -> Optional[WebsocketMetadata]:
        if not isinstance(metadataJson, Dict) or not utils.hasItems(metadataJson):
            return None

        messageTimestamp = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(metadataJson, 'message_timestamp')))
        messageId = utils.getStrFromDict(metadataJson, 'message_id')
        messageType = WebsocketMessageType.fromStr(utils.getStrFromDict(metadataJson, 'message_type'))

        subscriptionType: Optional[WebsocketSubscriptionType] = None
        if 'subscription_type' in metadataJson and utils.isValidStr(metadataJson.get('subscription_type')):
            subscriptionType = WebsocketSubscriptionType.fromStr(utils.getStrFromDict(metadataJson, 'subscription_type'))

        subscriptionVersion: Optional[str] = None
        if 'subscription_version' in metadataJson and utils.isValidStr(metadataJson.get('subscription_version')):
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

        event = await self.parseWebsocketEvent(payloadJson.get('event'))
        session = await self.parseWebsocketSession(payloadJson.get('session'))
        subscription = await self.parseWebsocketSubscription(payloadJson.get('subscription'))

        return WebsocketPayload(
            event = event,
            session = session,
            subscription  = subscription
        )

    async def __parseTransport(self, transportJson: Optional[Dict[str, Any]]) -> Optional[WebsocketTransport]:
        if not isinstance(transportJson, Dict) or not utils.hasItems(transportJson):
            return None

        connectedAt: Optional[SimpleDateTime] = None
        if 'connected_at' in transportJson and utils.isValidStr(transportJson.get('connected_at')):
            connectedAt = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(transportJson, 'connected_at')))

        disconnectedAt: Optional[SimpleDateTime] = None
        if 'disconnected_at' in transportJson and utils.isValidStr(transportJson.get('disconnected_at')):
            disconnectedAt = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(transportJson, 'disconnected_at')))

        secret: Optional[str] = None
        if 'secret' in transportJson and utils.isValidStr(transportJson.get('secret')):
            secret = utils.getStrFromDict(transportJson, 'secret')

        sessionId: Optional[str] = None
        if 'session_id' in transportJson and utils.isValidBool(transportJson.get('session_id')):
            sessionId = utils.getStrFromDict(transportJson, 'session_id')

        method = WebsocketTransportMethod.fromStr(utils.getStrFromDict(transportJson, 'method'))

        return WebsocketTransport(
            connectedAt = connectedAt,
            disconnectedAt = disconnectedAt,
            secret = secret,
            sessionId = sessionId,
            method = method
        )

    async def parseWebsocketDataBundle(self, dataBundleJson: Optional[Dict[str, Any]]) -> Optional[WebsocketDataBundle]:
        if not isinstance(dataBundleJson, Dict) or not utils.hasItems(dataBundleJson):
            return None

        metadata = await self.__parseMetadata(dataBundleJson.get('metadata'))

        if metadata is None:
            self.__timber.log('TwitchWebsocketJsonMapper', f'Websocket message ({dataBundleJson}) is missing \"metadata\" ({metadata}) field')
            return None

        payload = await self.__parsePayload(dataBundleJson.get('payload'))

        return WebsocketDataBundle(
            metadata = metadata,
            payload = payload
        )

    async def parseWebsocketEvent(self, eventJson: Optional[Dict[str, Any]]) -> Optional[WebsocketEvent]:
        if not isinstance(eventJson, Dict) or not utils.hasItems(eventJson):
            return None

        isAnonymous: Optional[bool] = None
        if 'is_anonymous' in eventJson and utils.isValidBool(eventJson.get('is_anonymous')):
            isAnonymous = utils.getBoolFromDict(eventJson, 'is_anonymous')

        isGift: Optional[bool] = None
        if 'is_gift' in eventJson and utils.isValidBool(eventJson.get('is_gift')):
            isGift = utils.getBoolFromDict(eventJson, 'is_gift')

        bits: Optional[int] = None
        if 'bits' in eventJson and utils.isValidInt(eventJson.get('bits')):
            bits = utils.getIntFromDict(eventJson, 'bits')

        cumulativeMonths: Optional[int] = None
        if 'cumulative_months' in eventJson and utils.isValidInt(eventJson.get('cumulative_months')):
            cumulativeMonths = utils.getIntFromDict(eventJson, 'cumulative_months')

        total: Optional[int] = None
        if 'total' in eventJson and utils.isValidInt(eventJson.get('total')):
            total = utils.getIntFromDict(eventJson, 'total')

        viewers: Optional[int] = None
        if 'viewers' in eventJson and utils.isValidInt(eventJson.get('viewers')):
            viewers = utils.getIntFromDict(eventJson, 'viewers')

        followedAt: Optional[SimpleDateTime] = None
        if 'followed_at' in eventJson and utils.isValidStr(eventJson.get('followed_at')):
            followedAt = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(eventJson, 'followed_at')))

        redeemedAt: Optional[SimpleDateTime] = None
        if 'redeemed_at' in eventJson and utils.isValidStr(eventJson.get('redeemed_at')):
            redeemedAt = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(eventJson, 'redeemed_at')))

        broadcasterUserId: Optional[str] = None
        if 'broadcaster_user_id' in eventJson and utils.isValidStr(eventJson.get('broadcaster_user_id')):
            broadcasterUserId = utils.getStrFromDict(eventJson, 'broadcaster_user_id')

        broadcasterUserLogin: Optional[str] = None
        if 'broadcaster_user_login' in eventJson and utils.isValidStr(eventJson.get('broadcaster_user_login')):
            broadcasterUserLogin = utils.getStrFromDict(eventJson, 'broadcaster_user_login')

        broadcasterUserName: Optional[str] = None
        if 'broadcaster_user_name' in eventJson and utils.isValidStr(eventJson.get('broadcaster_user_name')):
            broadcasterUserName = utils.getStrFromDict(eventJson, 'broadcaster_user_name')

        categoryId: Optional[str] = None
        if 'category_id' in eventJson and utils.isValidStr(eventJson.get('category_id')):
            categoryId = utils.getStrFromDict(eventJson, 'category_id')

        categoryName: Optional[str] = None
        if 'category_name' in eventJson and utils.isValidStr(eventJson.get('category_name')):
            categoryName = utils.getStrFromDict(eventJson, 'category_name')

        eventId: Optional[str] = None
        if 'id' in eventJson and utils.isValidStr(eventJson.get('id')):
            eventId = utils.getStrFromDict(eventJson, 'id')

        fromBroadcasterUserId: Optional[str] = None
        if 'from_broadcaster_user_id' in eventJson and utils.isValidStr(eventJson.get('from_broadcaster_user_id')):
            fromBroadcasterUserId = utils.getStrFromDict(eventJson, 'from_broadcaster_user_id')

        fromBroadcasterUserLogin: Optional[str] = None
        if 'from_broadcaster_user_login' in eventJson and utils.isValidStr(eventJson.get('from_broadcaster_user_login')):
            fromBroadcasterUserLogin = utils.getStrFromDict(eventJson, 'from_broadcaster_user_login')

        fromBroadcasterUserName: Optional[str] = None
        if 'from_broadcaster_user_name' in eventJson and utils.isValidStr(eventJson.get('from_broadcaster_user_name')):
            fromBroadcasterUserName = utils.getStrFromDict(eventJson, 'from_broadcaster_user_name')

        message: Optional[str] = None
        if 'message' in eventJson and utils.isValidStr(eventJson.get('message')):
            message = utils.getStrFromDict(eventJson, 'message')

        rewardId: Optional[str] = None
        if 'reward_id' in eventJson and utils.isValidStr(eventJson.get('reward_id')):
            rewardId = utils.getStrFromDict(eventJson, 'reward_id')

        text: Optional[str] = None
        if 'text' in eventJson and utils.isValidStr(eventJson.get('text')):
            text = utils.getStrFromDict(eventJson, 'text')

        title: Optional[str] = None
        if 'title' in eventJson and utils.isValidStr(eventJson.get('title')):
            title = utils.getStrFromDict(eventJson, 'title')

        toBroadcasterUserId: Optional[str] = None
        if 'to_broadcaster_user_id' in eventJson and utils.isValidStr(eventJson.get('to_broadcaster_user_id')):
            toBroadcasterUserId = utils.getStrFromDict(eventJson, 'to_broadcaster_user_id')

        toBroadcasterUserLogin: Optional[str] = None
        if 'to_broadcaster_user_login' in eventJson and utils.isValidStr(eventJson.get('to_broadcaster_user_login')):
            toBroadcasterUserLogin = utils.getStrFromDict(eventJson, 'to_broadcaster_user_login')

        toBroadcasterUserName: Optional[str] = None
        if 'to_broadcaster_user_name' in eventJson and utils.isValidStr(eventJson.get('to_broadcaster_user_name')):
            toBroadcasterUserName = utils.getStrFromDict(eventJson, 'to_broadcaster_user_name')

        userId: Optional[str] = None
        if 'user_id' in eventJson and utils.isValidStr(eventJson.get('user_id')):
            userId = utils.getStrFromDict(eventJson, 'user_id')

        userInput: Optional[str] = None
        if 'user_input' in eventJson and utils.isValidStr(eventJson.get('user_input')):
            userInput = utils.getStrFromDict(eventJson, 'user_input')

        userLogin: Optional[str] = None
        if 'user_login' in eventJson and utils.isValidStr(eventJson.get('user_login')):
            userLogin = utils.getStrFromDict(eventJson, 'user_login')

        userName: Optional[str] = None
        if 'user_name' in eventJson and utils.isValidStr(eventJson.get('user_name')):
            userName = utils.getStrFromDict(eventJson, 'user_name')

        tier: Optional[TwitchSubscriberTier] = None
        if 'tier' in eventJson and utils.isValidStr(eventJson.get('tier')):
            tier = TwitchSubscriberTier.fromStr(utils.getStrFromDict(eventJson, 'tier'))

        return WebsocketEvent(
            isAnonymous = isAnonymous,
            isGift = isGift,
            bits = bits,
            cumulativeMonths = cumulativeMonths,
            total = total,
            viewers = viewers,
            followedAt = followedAt,
            redeemedAt = redeemedAt,
            broadcasterUserId = broadcasterUserId,
            broadcasterUserLogin = broadcasterUserLogin,
            broadcasterUserName = broadcasterUserName,
            categoryId = categoryId,
            categoryName = categoryName,
            eventId = eventId,
            fromBroadcasterUserId = fromBroadcasterUserId,
            fromBroadcasterUserLogin = fromBroadcasterUserLogin,
            fromBroadcasterUserName = fromBroadcasterUserName,
            message = message,
            rewardId = rewardId,
            text = text,
            title = title,
            toBroadcasterUserId = toBroadcasterUserId,
            toBroadcasterUserLogin = toBroadcasterUserLogin,
            toBroadcasterUserName = toBroadcasterUserName,
            userId = userId,
            userInput = userInput,
            userLogin = userLogin,
            userName = userName,
            tier = tier
        )

    async def parseWebsocketReward(self, rewardJson: Optional[Dict[str, Any]]) -> Optional[WebsocketReward]:
        if not isinstance(rewardJson, Dict) or not utils.hasItems(rewardJson):
            return None

        cost = utils.getIntFromDict(rewardJson, 'cost')

        prompt: Optional[str] = None
        if 'prompt' in rewardJson and utils.isValidStr(rewardJson.get('prompt')):
            prompt = utils.getStrFromDict(rewardJson, 'prompt')

        rewardId = utils.getStrFromDict(rewardJson, 'reward_id')
        title = utils.getStrFromDict(rewardJson, 'title')

        return WebsocketReward(
            cost = cost,
            prompt = prompt,
            rewardId = rewardId,
            title = title
        )

    async def parseWebsocketSession(self, sessionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketSession]:
        if not isinstance(sessionJson, Dict) or not utils.hasItems(sessionJson):
            return None

        keepAliveTimeoutSeconds = utils.getIntFromDict(sessionJson, 'keepalive_timeout_seconds')
        connectedAt = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(sessionJson, 'connected_at')))
        sessionId = utils.getStrFromDict(sessionJson, 'id')
        status = WebsocketConnectionStatus.fromStr(utils.getStrFromDict(sessionJson, 'status'))

        if 'reconnect_url' in sessionJson and utils.isValidUrl(sessionJson.get('reconnect_url')):
            reconnectUrl = utils.getStrFromDict(sessionJson, 'reconnect_url')

        return WebsocketSession(
            keepAliveTimeoutSeconds = keepAliveTimeoutSeconds,
            connectedAt = connectedAt,
            reconnectUrl = reconnectUrl,
            sessionId = sessionId,
            status = status
        )

    async def parseWebsocketSubscription(self, subscriptionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketSubscription]:
        if not isinstance(subscriptionJson, Dict) or not utils.hasItems(subscriptionJson):
            return None

        cost = utils.getIntFromDict(subscriptionJson, 'cost')
        createdAt = SimpleDateTime(utils.getDateTimeFromStr(utils.getStrFromDict(subscriptionJson, 'created_at')))
        subscriptionId = utils.getStrFromDict(subscriptionJson, 'id')
        version = utils.getStrFromDict(subscriptionJson, 'version')
        condition = await self.parseWebsocketCondition(subscriptionJson.get('condition'))
        status = WebsocketConnectionStatus.fromStr(utils.getStrFromDict(subscriptionJson, 'status'))
        subscriptionType = WebsocketSubscriptionType.fromStr(utils.getStrFromDict(subscriptionJson, 'type'))
        transport = await self.__parseTransport(subscriptionJson.get('transport'))

        return WebsocketSubscription(
            cost = cost,
            createdAt = createdAt,
            subscriptionId = subscriptionId,
            version = version,
            condition = condition,
            status = status,
            subscriptionType = subscriptionType,
            transport = transport
        )
