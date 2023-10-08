try:
    from ..websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus
except:
    from twitch.websocket.websocketSubscriptionStatus import \
        WebsocketSubscriptionStatus


class TestTwitchWebsocketSubscriptionStatus():

    def test_fromStr_withAdminString(self):
        result = WebsocketSubscriptionStatus.fromStr('connected')
        assert result is WebsocketSubscriptionStatus.CONNECTED

    def test_fromStr_withAuthorizationRevokedString(self):
        result = WebsocketSubscriptionStatus.fromStr('authorization_revoked')
        assert result is WebsocketSubscriptionStatus.REVOKED

    def test_fromStr_withEmptyString(self):
        result = WebsocketSubscriptionStatus.fromStr('')
        assert result is None

    def test_fromStr_withGlobalModString(self):
        result = WebsocketSubscriptionStatus.fromStr('enabled')
        assert result is WebsocketSubscriptionStatus.ENABLED

    def test_fromStr_withNone(self):
        result = WebsocketSubscriptionStatus.fromStr(None)
        assert result is None

    def test_fromStr_withStaffString(self):
        result = WebsocketSubscriptionStatus.fromStr('reconnecting')
        assert result is WebsocketSubscriptionStatus.RECONNECTING

    def test_fromStr_withWhitespaceString(self):
        result = WebsocketSubscriptionStatus.fromStr(' ')
        assert result is None
