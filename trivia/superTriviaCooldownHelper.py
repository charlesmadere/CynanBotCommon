from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class SuperTriviaCooldownHelper():

    def __init__(self, triviaSettingsRepository: TriviaSettingsRepository):
        if triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__values: Dict[str, datetime] = defaultdict(lambda: datetime.now(timezone.utc) - timedelta(days = 1))

    def __getitem__(self, key: str) -> bool:
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        now = datetime.now(timezone.utc)
        return now > self.__values[key.lower()]

    async def update(self, key: str):
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        cooldownSeconds = await self.__triviaSettingsRepository.getSuperTriviaCooldownSeconds()
        cooldown = timedelta(seconds = cooldownSeconds)
        now = datetime.now(timezone.utc)

        self.__values[key.lower()] = now + cooldown
