try:
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ..websocket.twitchWebsocketJsonMapper import TwitchWebsocketJsonMapper
    from ..websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
except:
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub

    from twitch.websocket.twitchWebsocketJsonMapper import \
        TwitchWebsocketJsonMapper
    from twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface


class TestTwitchWebsocketJsonMapper():

    timber: TimberInterface = TimberStub()

    jsonMapper: TwitchWebsocketJsonMapperInterface = TwitchWebsocketJsonMapper(
        timber = timber
    )

    def test_sanity(self):
        assert self.jsonMapper is not None
        assert isinstance(self.jsonMapper, TwitchWebsocketJsonMapperInterface)
