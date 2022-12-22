import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cuteness.cutenessRepository import CutenessRepository
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.shinyTriviaOccurencesRepository import \
        ShinyTriviaOccurencesRepository
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils
    from cuteness.cutenessRepository import CutenessRepository
    from timber.timber import Timber
    from trivia.shinyTriviaOccurencesRepository import \
        ShinyTriviaOccurencesRepository
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class ShinyTriviaHelper():

    def __init__(
        self,
        cutenessRepository: CutenessRepository,
        shinyTriviaOccurencesRepository: ShinyTriviaOccurencesRepository,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        cooldown: timedelta = timedelta(hours = 2),
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(cutenessRepository, CutenessRepository):
            raise ValueError(f'cutenessRepository argument is malformed: \"{cutenessRepository}\"')
        elif not isinstance(shinyTriviaOccurencesRepository, ShinyTriviaOccurencesRepository):
            raise ValueError(f'shinyTriviaOccurencesRepository argument is malformed: \"{shinyTriviaOccurencesRepository}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not isinstance(cooldown, timedelta):
            raise ValueError(f'cooldown argument is malformed: \"{cooldown}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__cutenessRepository: CutenessRepository = cutenessRepository
        self.__shinyTriviaOccurencesRepository: ShinyTriviaOccurencesRepository = shinyTriviaOccurencesRepository
        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__cooldown: timedelta = cooldown
        self.__timeZone: timezone = timeZone

        self.__rankToProbabilityDict: Dict[int, float] = self.__createRankToProbabilityDict()

    def __createRankToProbabilityDict(self) -> Dict[int, float]:
        values: Dict[int, float] = dict()
        values[1] =  0.001
        values[2] =  0.010
        values[3] =  0.100
        values[4] =  0.200
        values[5] =  0.300
        values[6] =  0.400
        values[7] =  0.500
        values[8] =  0.700
        values[9] =  0.950

        return values

    async def __getUserPlacementOnLeaderboard(
        self,
        twitchChannel: str,
        userId: str
    ) -> Optional[int]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        cutenessLeaderboard = await self.__cutenessRepository.fetchCutenessLeaderboard(
            twitchChannel = twitchChannel
        )

        if not cutenessLeaderboard.hasEntries():
            return None

        userId = userId.lower()

        for entry in cutenessLeaderboard.getEntries():
            if entry.getUserId().lower() == userId:
                return entry.getRank()

        return None

    async def isShinyTriviaQuestion(self, twitchChannel: str, userId: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        if not await self.__triviaSettingsRepository.areShiniesEnabled():
            return False

        userPlacementOnLeaderboard = await self.__getUserPlacementOnLeaderboard(
            twitchChannel = twitchChannel,
            userId = userId
        )

        probability = await self.__triviaSettingsRepository.getShinyProbability()

        if userPlacementOnLeaderboard is not None and userPlacementOnLeaderboard in self.__rankToProbabilityDict:
            probability = probability * self.__rankToProbabilityDict[userPlacementOnLeaderboard]

        if random.uniform(0, 1) > probability:
            return False

        details = await self.__shinyTriviaOccurencesRepository.fetchDetails(
            twitchChannel = twitchChannel,
            userId = userId
        )

        if details.getMostRecent() is not None:
            now = datetime.now(self.__timeZone)

            if now - details.getMostRecent() < self.__cooldown:
                self.__timber.log('ShinyTriviaHelper', f'{details.getUserName()}:{details.getUserId()} in {details.getTwitchChannel()} would have encountered a shiny, but it was rejected, as their most recent shiny ({details.getMostRecent()}) is within the cooldown time')
                return False

        result = await self.__shinyTriviaOccurencesRepository.incrementShinyCount(
            twitchChannel = twitchChannel,
            userId = userId
        )

        self.__timber.log('ShinyTriviaHelper', f'{result.getUserName()}:{result.getUserId()} in {twitchChannel} has encountered a shiny!')

        return True

    async def isShinySuperTriviaQuestion(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if not await self.__triviaSettingsRepository.areShiniesEnabled():
            return False        

        probability = await self.__triviaSettingsRepository.getShinyProbability()

        if random.uniform(0, 1) > probability:
            return False

        self.__timber.log('ShinyTriviaHelper', f'{twitchChannel} has encountered a shiny!')

        return True
