from typing import Dict, Optional

try:
    from ..twitchEventSubRequest import TwitchEventSubRequest
    from ..websocket.websocketSubscriptionType import WebsocketSubscriptionType
    from ..websocket.websocketTransport import WebsocketTransport
    from ..websocket.websocketTransportMethod import WebsocketTransportMethod
    from ..websocket.websocketCondition import WebsocketCondition
except:
    from twitch.twitchEventSubRequest import TwitchEventSubRequest
    from websocket.websocketCondition import WebsocketCondition
    from websocket.websocketTransportMethod import WebsocketTransportMethod
    from websocket.websocketTransport import WebsocketTransport
    from websocket.websocketSubscriptionType import WebsocketSubscriptionType


class TestTwitchEventSubRequest():

    def test_toJson1(self):
        condition = WebsocketCondition(
            broadcasterUserId = 'abc123'
        )

        subscriptionType = WebsocketSubscriptionType.CHANNEL_POINTS_REDEMPTION

        transport = WebsocketTransport(
            method = WebsocketTransportMethod.WEBSOCKET,
            sessionId = 'qwerty'
        )

        request = TwitchEventSubRequest(
            condition = condition,
            subscriptionType = subscriptionType,
            transport = transport
        )

        dictionary = request.toJson()

        assert isinstance(dictionary, Dict)

        assert 'condition' in dictionary
        assert 'broadcaster_user_id' in dictionary['condition']
        assert condition.getBroadcasterUserId() == dictionary['condition']['broadcaster_user_id']

        assert 'transport' in dictionary
        assert 'method' in dictionary['transport']
        assert dictionary['transport']['method'] == transport.getMethod().toStr()
        assert 'session_id' in dictionary['transport']
        assert dictionary['transport']['session_id'] == transport.getSessionId()

        assert 'type' in dictionary
        assert dictionary['type'] == subscriptionType.toStr()

        assert 'version' in dictionary
        assert dictionary['version'] == subscriptionType.getVersion()


    def test_toJson2(self):
        condition = WebsocketCondition(
            broadcasterUserId = 'def987'
        )

        subscriptionType = WebsocketSubscriptionType.SUBSCRIBE

        transport = WebsocketTransport(
            method = WebsocketTransportMethod.WEBSOCKET,
            sessionId = 'azerty'
        )

        request = TwitchEventSubRequest(
            condition = condition,
            subscriptionType = subscriptionType,
            transport = transport
        )

        dictionary = request.toJson()

        assert isinstance(dictionary, Dict)

        assert 'condition' in dictionary
        assert 'broadcaster_user_id' in dictionary['condition']
        assert condition.getBroadcasterUserId() == dictionary['condition']['broadcaster_user_id']

        assert 'transport' in dictionary
        assert 'method' in dictionary['transport']
        assert dictionary['transport']['method'] == transport.getMethod().toStr()
        assert 'session_id' in dictionary['transport']
        assert dictionary['transport']['session_id'] == transport.getSessionId()

        assert 'type' in dictionary
        assert dictionary['type'] == subscriptionType.toStr()

        assert 'version' in dictionary
        assert dictionary['version'] == subscriptionType.getVersion()
