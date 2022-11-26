from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

try:
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    from timber.timber import Timber
    from trivia.triviaSource import TriviaSource


class TriviaSourceInstabilityHelper():

    def __init__(
        self,
        timber: Timber,
        fallOffTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif fallOffTimeDelta is None:
            raise ValueError(f'fallOffTimeDelta argument is malformed: \"{fallOffTimeDelta}\"')

        self.__timber: Timber = timber
        self.__fallOffTimeDelta: timedelta = fallOffTimeDelta

        self.__times: Dict[TriviaSource, Optional[datetime]] = dict()
        self.__values: Dict[TriviaSource, int] = defaultdict(lambda: 0)

    def __getitem__(self, key: TriviaSource) -> int:
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        now = datetime.now(timezone.utc)
        lastErrorTime = self.__times.get(key, None)

        if lastErrorTime is not None and now - lastErrorTime <= self.__fallOffTimeDelta:
            return self.__values[key]

        self.__values[key] = 0
        return 0

    def incrementErrorCount(self, key: TriviaSource) -> int:
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        now = datetime.now(timezone.utc)
        lastErrorTime = self.__times.get(key, None)
        self.__times[key] = now
        newErrorCount: int = 0

        if lastErrorTime is not None and now - lastErrorTime <= self.__fallOffTimeDelta:
            newErrorCount = self.__values[key] + 1
            self.__values[key] = newErrorCount
        else:
            newErrorCount = 1
            self.__values[key] = newErrorCount

        self.__timber.log('TriviaSourceInstabilityHelper', f'Incremented error count for {key} to {newErrorCount}')
        return newErrorCount
