try:
    from ..websocket.websocketConditionStatus import WebsocketConditionStatus
except:
    from twitch.websocket.websocketConditionStatus import \
        WebsocketConditionStatus


class TestTwitchWebsocketConditionStatus():

    def test_fromStr_withCanceledString(self):
        result = WebsocketConditionStatus.fromStr('canceled')
        assert result is WebsocketConditionStatus.CANCELED

    def test_fromStr_withCancelledString(self):
        result = WebsocketConditionStatus.fromStr('cancelled')
        assert result is WebsocketConditionStatus.CANCELED

    def test_fromStr_withEmptyString(self):
        result = WebsocketConditionStatus.fromStr('')
        assert result is WebsocketConditionStatus.UNKNOWN

    def test_fromStr_withFulfilledString(self):
        result = WebsocketConditionStatus.fromStr('fulfilled')
        assert result is WebsocketConditionStatus.FULFILLED

    def test_fromStr_withNone(self):
        result = WebsocketConditionStatus.fromStr(None)
        assert result is WebsocketConditionStatus.UNKNOWN

    def test_fromStr_withUnfulfilledString(self):
        result = WebsocketConditionStatus.fromStr('unfulfilled')
        assert result is WebsocketConditionStatus.UNFULFILLED

    def test_fromStr_withWhitespaceString(self):
        result = WebsocketConditionStatus.fromStr(' ')
        assert result is WebsocketConditionStatus.UNKNOWN
