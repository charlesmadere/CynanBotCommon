from typing import Optional

try:
    from ..websocket.websocketTransport import (WebsocketTransport,
                                                WebsocketTransportMethod)
except:
    from twitch.websocket.websocketTransport import (WebsocketTransport,
                                                     WebsocketTransportMethod)


class TestTwitchWebsocketTransport():

    def test_requireSessionId_withEmptyString(self):
        transport = WebsocketTransport(
            sessionId = '',
            method = WebsocketTransportMethod.WEBSOCKET
        )

        sessionId: Optional[str] = None
        exception: Optional[Exception] = None

        try:
            sessionId = transport.requireSessionId()
        except Exception as e:
            exception = e

        assert sessionId is None
        assert isinstance(exception, Exception)

    def test_requireSessionId_withNone(self):
        transport = WebsocketTransport(
            method = WebsocketTransportMethod.WEBSOCKET
        )
        sessionId: Optional[str] = None
        exception: Optional[Exception] = None

        try:
            sessionId = transport.requireSessionId()
        except Exception as e:
            exception = e

        assert sessionId is None
        assert isinstance(exception, Exception)

    def test_requireSessionId_withValidString(self):
        transport = WebsocketTransport(
            sessionId = 'abc123',
            method = WebsocketTransportMethod.WEBSOCKET
        )

        assert transport.requireSessionId() == 'abc123'

    def test_requireSessionId_withWhitespaceString(self):
        transport = WebsocketTransport(
            sessionId = ' ',
            method = WebsocketTransportMethod.WEBSOCKET
        )

        sessionId: Optional[str] = None
        exception: Optional[Exception] = None

        try:
            sessionId = transport.requireSessionId()
        except Exception as e:
            exception = e

        assert sessionId is None
        assert isinstance(exception, Exception)
