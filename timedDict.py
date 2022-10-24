from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TimedDict():

    def __init__(self, timeDelta: timedelta):
        if timeDelta is None:
            raise ValueError(f'timeDelta argument is malformed: \"{timeDelta}\"')

        self.__timeDelta: timedelta = timeDelta
        self.__times: Dict[str, Any] = dict()
        self.__values: Dict[str, Any] = dict()

    def clear(self):
        self.__times.clear()
        self.__values.clear()

    def __delitem__(self, key: str):
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        self.__times.pop(key, None)
        self.__values.pop(key, None)

    def __getitem__(self, key: str) -> Optional[Any]:
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        if key not in self.__times or key not in self.__values:
            return None

        nowDateTime = datetime.now(timezone.utc)

        if nowDateTime > self.__times[key]:
            return None

        return self.__values[key]

    def isReady(self, key: str) -> bool:
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        return self[key] is None

    def isReadyAndUpdate(self, key: str) -> bool:
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        if self.isReady(key):
            self.update(key)
            return True
        else:
            return False

    def __setitem__(self, key: str, value):
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        self.__times[key] = datetime.now(timezone.utc) + self.__timeDelta
        self.__values[key] = value

    def update(self, key: str):
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        self.__times[key] = datetime.now(timezone.utc) + self.__timeDelta
        self.__values[key] = self.__times[key]
