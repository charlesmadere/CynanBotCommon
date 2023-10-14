from typing import Optional

try:
    from ..websocket.websocketTransport import WebsocketTransport
except:
    from twitch.websocket.websocketTransport import WebsocketTransport


class TestTwitchWebsocketTransport():

    def test_requireSessionId_withEmptyString(self):
        transport = WebsocketTransport(
            sessionId = ''
        )

        sessionId: Optional[str] = None
        exception: Optional[Exception] = None

        try:
            sessionId = transport.requireSessionId()
        except Exception as e:
            exception = e

        assert sessionId is None
        assert isinstance(exception, Exception)

    def test_requireBroadcasterUserId_withNone(self):
        transport = WebsocketTransport()
        broadcasterUserId: Optional[str] = None
        exception: Optional[Exception] = None

        try:
            broadcasterUserId = transport.requireSessionId()
        except Exception as e:
            exception = e

        assert broadcasterUserId is None
        assert isinstance(exception, Exception)

    def test_requireBroadcasterUserId_withValidString(self):
        transport = WebsocketTransport(
            broadcasterUserId = 'abc123'
        )

        assert transport.requireSessionId() == 'abc123'

    def test_requireBroadcasterUserId_withWhitespaceString(self):
        transport = WebsocketTransport(
            broadcasterUserId = ' '
        )

        broadcasterUserId: Optional[str] = None
        exception: Optional[Exception] = None

        try:
            broadcasterUserId = transport.requireSessionId()
        except Exception as e:
            exception = e

        assert broadcasterUserId is None
        assert isinstance(exception, Exception)
