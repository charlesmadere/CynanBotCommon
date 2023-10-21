from typing import Optional

import pytest

try:
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ..websocket.twitchWebsocketJsonMapper import TwitchWebsocketJsonMapper
    from ..websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from ..websocket.websocketCondition import WebsocketCondition
    from ..websocket.websocketEvent import WebsocketEvent
    from ..websocket.websocketReward import WebsocketReward
    from ..websocket.websocketSession import WebsocketSession
    from ..websocket.websocketSubscription import WebsocketSubscription
except:
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub

    from twitch.websocket.twitchWebsocketJsonMapper import \
        TwitchWebsocketJsonMapper
    from twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketEvent import WebsocketEvent
    from twitch.websocket.websocketReward import WebsocketReward
    from twitch.websocket.websocketSession import WebsocketSession
    from twitch.websocket.websocketSubscription import WebsocketSubscription


class TestTwitchWebsocketJsonMapper():

    timber: TimberInterface = TimberStub()

    jsonMapper: TwitchWebsocketJsonMapperInterface = TwitchWebsocketJsonMapper(
        timber = timber
    )

    @pytest.mark.asyncio
    async def test_parseWebsocketCondition_withEmptyDictionary(self):
        result = await self.jsonMapper.parseWebsocketCondition(dict())
        assert isinstance(result, WebsocketCondition)
        assert result.getBits() is None
        assert result.getBroadcasterUserId() is None
        assert result.getBroadcasterUserLogin() is None
        assert result.getBroadcasterUserName() is None
        assert result.getCategoryId() is None
        assert result.getCategoryName() is None
        assert result.getClientId() is None
        assert result.getCumulativeTotal() is None
        assert result.getFromBroadcasterUserId() is None
        assert result.getFromBroadcasterUserLogin() is None
        assert result.getFromBroadcasterUserName() is None
        assert result.getMessage() is None
        assert result.getModeratorUserId() is None
        assert result.getModeratorUserLogin() is None
        assert result.getModeratorUserName() is None
        assert result.getReason() is None
        assert result.getReward() is None
        assert result.getRewardId() is None
        assert result.getTier() is None
        assert result.getTitle() is None
        assert result.getToBroadcasterUserId() is None
        assert result.getToBroadcasterUserLogin() is None
        assert result.getToBroadcasterUserName() is None
        assert result.getTotal() is None
        assert result.getUserId() is None
        assert result.getUserInput() is None
        assert result.getUserLogin() is None
        assert result.getUserName() is None
        assert result.getViewers() is None
        assert result.isAnonymous() is None
        assert result.isGift() is None
        assert result.isPermanent() is None

        broadcasterUserId: Optional[str] = None
        exception: Optional[Exception] = None

        try:
            broadcasterUserId = result.requireBroadcasterUserId()
        except Exception as e:
            exception = e

        assert broadcasterUserId is None
        assert isinstance(exception, Exception)

    @pytest.mark.asyncio
    async def test_parseWebsocketCondition_withNone(self):
        result = await self.jsonMapper.parseWebsocketCondition(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_parseWebsocketDataBundle_withEmptyDictionary(self):
        result = await self.jsonMapper.parseWebsocketDataBundle(dict())
        assert result is None

    @pytest.mark.asyncio
    async def test_parseWebsocketDataBundle_withNone(self):
        result = await self.jsonMapper.parseWebsocketDataBundle(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_parseWebsocketEvent_withEmptyDictionary(self):
        result = await self.jsonMapper.parseWebsocketEvent(dict())
        assert isinstance(result, WebsocketEvent)

    @pytest.mark.asyncio
    async def test_parseWebsocketEvent_withNone(self):
        result = await self.jsonMapper.parseWebsocketEvent(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_parseWebsocketReward_withEmptyDictionary(self):
        result = await self.jsonMapper.parseWebsocketReward(dict())
        assert isinstance(result, WebsocketReward)

    @pytest.mark.asyncio
    async def test_parseWebsocketReward_withNone(self):
        result = await self.jsonMapper.parseWebsocketReward(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_parseWebsocketSession_withEmptyDictionary(self):
        result = await self.jsonMapper.parseWebsocketSession(dict())
        assert isinstance(result, WebsocketSession)

    @pytest.mark.asyncio
    async def test_parseWebsocketSession_withNone(self):
        result = await self.jsonMapper.parseWebsocketSession(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_parseWebsocketSubscription_withEmptyDictionary(self):
        result = await self.jsonMapper.parseWebsocketSubscription(dict())
        assert isinstance(result, WebsocketSubscription)

    @pytest.mark.asyncio
    async def test_parseWebsocketSubscription_withEmptyDictionary(self):
        result = await self.jsonMapper.parseWebsocketSubscription(None)
        assert result is None

    def test_sanity(self):
        assert self.jsonMapper is not None
        assert isinstance(self.jsonMapper, TwitchWebsocketJsonMapperInterface)
