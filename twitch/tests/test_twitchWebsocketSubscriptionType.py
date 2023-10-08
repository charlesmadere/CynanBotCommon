try:
    from ..websocket.websocketSubscriptionType import WebsocketSubscriptionType
except:
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType


class TestTwitchWebsocketSubscriptionType():

    def test_fromStr_withChannelUpdateString(self):
        result = WebsocketSubscriptionType.fromStr('channel.update')
        assert result is WebsocketSubscriptionType.CHANNEL_UPDATE

    def test_fromStr_withChannelFollowString(self):
        result = WebsocketSubscriptionType.fromStr('channel.follow')
        assert result is WebsocketSubscriptionType.FOLLOW

    def test_fromStr_withChannelSubscribeString(self):
        result = WebsocketSubscriptionType.fromStr('channel.subscribe')
        assert result is WebsocketSubscriptionType.SUBSCRIBE

    def test_fromStr_withEmptyString(self):
        result = WebsocketSubscriptionType.fromStr('')
        assert result is None

    def test_fromStr_withNone(self):
        result = WebsocketSubscriptionType.fromStr(None)
        assert result is None

    def test_fromStr_withStreamsOnlineString(self):
        result = WebsocketSubscriptionType.fromStr('streams.online')
        assert result is WebsocketSubscriptionType.STREAMS_ONLINE

    def test_fromStr_withStreamsOnlineString(self):
        result = WebsocketSubscriptionType.fromStr('channel.subscription.gift')
        assert result is WebsocketSubscriptionType.SUB_GIFT

    def test_fromStr_withWhitespaceString(self):
        result = WebsocketSubscriptionType.fromStr(' ')
        assert result is None
