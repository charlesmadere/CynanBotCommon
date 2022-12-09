import asyncio
from asyncio import AbstractEventLoop

import pytest

try:
    from ...timber.timber import Timber
    from ...trivia.addQueuedGamesResult import AddQueuedGamesResult
    from ...trivia.clearQueuedGamesResult import ClearQueuedGamesResult
    from ...trivia.queuedTriviaGameStore import QueuedTriviaGameStore
    from ...trivia.triviaSettingsRepository import TriviaSettingsRepository
except:
    from timber.timber import Timber
    from trivia.addQueuedGamesResult import AddQueuedGamesResult
    from trivia.clearQueuedGamesResult import ClearQueuedGamesResult
    from trivia.queuedTriviaGameStore import QueuedTriviaGameStore
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class TestQueuedTriviaGameStore():

    eventLoop: AbstractEventLoop = asyncio.get_event_loop()
    timber = Timber(
        eventLoop = eventLoop
    )
    triviaSettingsRepository = TriviaSettingsRepository()
    queuedTriviaGameStore = QueuedTriviaGameStore(
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_getQeuedSuperGamesSize_withEmptyTwitchChannel_isZero(self):
        size = await self.queuedTriviaGameStore.getQueuedSuperGamesSize('oatsngoats')
        assert size == 0
