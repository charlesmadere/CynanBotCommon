from typing import Optional

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
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if not isinstance(cutenessRepository, CutenessRepository):
            raise ValueError(f'cutenessRepository argument is malformed: \"{cutenessRepository}\"')
        elif not isinstance(shinyTriviaOccurencesRepository, ShinyTriviaOccurencesRepository):
            raise ValueError(f'shinyTriviaOccurencesRepository argument is malformed: \"{shinyTriviaOccurencesRepository}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__cutenessRepository: CutenessRepository = cutenessRepository
        self.__shinyTriviaOccurencesRepository: ShinyTriviaOccurencesRepository = shinyTriviaOccurencesRepository
        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

    async def __getUserPlacementOnLeaderboard(
        self,
        twitchChannel: str,
        userId: str
    ) -> Optional[int]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        # TODO

        raise NotImplementedError()

    async def isShinyTriviaQuestion(
        self,
        twitchChannel: str,
        userId: str
    ) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        # TODO

        raise NotImplementedError()
