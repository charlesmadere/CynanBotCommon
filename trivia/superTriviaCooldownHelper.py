from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class SuperTriviaCooldownHelper():

    def __init__(
        self,
        triviaSettingsRepository: TriviaSettingsRepository,
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__timeZone: timezone = timeZone

        self.__values: Dict[str, datetime] = defaultdict(lambda: datetime.now(timeZone) - timedelta(days = 1))

    def __getitem__(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        now = datetime.now(self.__timeZone)
        return now > self.__values[twitchChannel.lower()]

    async def getTwitchChannelsInCooldown(self) -> List[str]:
        twitchChannels: Set[str] = set()
        now = datetime.now(self.__timeZone)

        for twitchChannel, cooldown in self.__values.items():
            if cooldown > now:
                twitchChannels.add(twitchChannel.lower())

        return list(twitchChannels)

    async def update(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        cooldownSeconds = await self.__triviaSettingsRepository.getSuperTriviaCooldownSeconds()
        cooldown = timedelta(seconds = cooldownSeconds)
        now = datetime.now(self.__timeZone)

        self.__values[twitchChannel.lower()] = now + cooldown
