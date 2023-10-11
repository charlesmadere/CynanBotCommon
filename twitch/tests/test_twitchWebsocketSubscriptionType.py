try:
    from ..websocket.websocketSubscriptionType import WebsocketSubscriptionType
except:
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType


class TestTwitchWebsocketSubscriptionType():

    def test_fromStr_withChannelChannelPointsCustomRewardRedemptionString(self):
        result = WebsocketSubscriptionType.fromStr('channel.channel_points_custom_reward_redemption.add')
        assert result is WebsocketSubscriptionType.CHANNEL_POINTS_REDEMPTION

    def test_fromStr_withChannelCheerString(self):
        result = WebsocketSubscriptionType.fromStr('channel.cheer')
        assert result is WebsocketSubscriptionType.CHEER

    def test_fromStr_withChannelFollowString(self):
        result = WebsocketSubscriptionType.fromStr('channel.follow')
        assert result is WebsocketSubscriptionType.FOLLOW

    def test_fromStr_withChannelRaidString(self):
        result = WebsocketSubscriptionType.fromStr('channel.raid')
        assert result is WebsocketSubscriptionType.RAID

    def test_fromStr_withChannelSubscribeString(self):
        result = WebsocketSubscriptionType.fromStr('channel.subscribe')
        assert result is WebsocketSubscriptionType.SUBSCRIBE

    def test_fromStr_withChannelSubscriptionGiftString(self):
        result = WebsocketSubscriptionType.fromStr('channel.subscription.gift')
        assert result is WebsocketSubscriptionType.SUBSCRIPTION_GIFT

    def test_fromStr_withChannelSubscriptionMessageString(self):
        result = WebsocketSubscriptionType.fromStr('channel.subscription.message')
        assert result is WebsocketSubscriptionType.SUBSCRIPTION_MESSAGE

    def test_fromStr_withChannelUpdateString(self):
        result = WebsocketSubscriptionType.fromStr('channel.update')
        assert result is WebsocketSubscriptionType.CHANNEL_UPDATE

    def test_fromStr_withEmptyString(self):
        result = WebsocketSubscriptionType.fromStr('')
        assert result is None

    def test_fromStr_withNone(self):
        result = WebsocketSubscriptionType.fromStr(None)
        assert result is None

    def test_fromStr_withStreamOfflineString(self):
        result = WebsocketSubscriptionType.fromStr('stream.offline')
        assert result is WebsocketSubscriptionType.STREAM_OFFLINE

    def test_fromStr_withStreamOnlineString(self):
        result = WebsocketSubscriptionType.fromStr('stream.online')
        assert result is WebsocketSubscriptionType.STREAM_ONLINE

    def test_fromStr_withWhitespaceString(self):
        result = WebsocketSubscriptionType.fromStr(' ')
        assert result is None
