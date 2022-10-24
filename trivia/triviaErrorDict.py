from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict

try:
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    from trivia.triviaSource import TriviaSource


class TriviaErrorDict():

    def __init__(self, fallOffTimeDelta: timedelta):
        if fallOffTimeDelta is None:
            raise ValueError(f'fallOffTimeDelta argument is malformed: \"{fallOffTimeDelta}\"')

        self.__fallOffTimeDelta: timedelta = fallOffTimeDelta
        self.__times: Dict[TriviaSource, datetime] = defaultdict(lambda: datetime(1970, 1, 1))
        self.__values: Dict[TriviaSource, int] = defaultdict(lambda: 0)

    def __delitem__(self, key: TriviaSource):
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        raise RuntimeError(f'this method is not supported for TriviaErrorDict')

    def __getitem__(self, key: TriviaSource) -> int:
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        now = datetime.now(timezone.utc)
        lastErrorTime = self.__times[key]

        if now - lastErrorTime <= self.__fallOffTimeDelta:
            return self.__values[key]

        self.__values[key] = 0
        return 0

    def incrementErrorCount(self, key: TriviaSource):
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        now = datetime.now(timezone.utc)
        lastErrorTime = self.__times[key]
        self.__times[key] = now

        if now - lastErrorTime <= self.__fallOffTimeDelta:
            self.__values[key] = self.__values[key] + 1
        else:
            self.__values[key] = 1

    def __setitem__(self, key: TriviaSource, value: int):
        if key is None or not isinstance(key, TriviaSource):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        raise RuntimeError(f'this method is not supported for TriviaErrorDict')
