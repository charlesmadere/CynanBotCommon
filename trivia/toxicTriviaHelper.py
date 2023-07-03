import random

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.toxicTriviaOccurencesRepository import \
        ToxicTriviaOccurencesRepository
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils
    from timber.timberInterface import TimberInterface
    from trivia.toxicTriviaOccurencesRepository import \
        ToxicTriviaOccurencesRepository
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class ToxicTriviaHelper():

    def __init__(
        self,
        toxicTriviaOccurencesRepository: ToxicTriviaOccurencesRepository,
        timber: TimberInterface,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if not isinstance(toxicTriviaOccurencesRepository, ToxicTriviaOccurencesRepository):
            raise ValueError(f'toxicTriviaOccurencesRepository argument is malformed: \"{toxicTriviaOccurencesRepository}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__toxicTriviaOccurencesRepository: ToxicTriviaOccurencesRepository = toxicTriviaOccurencesRepository
        self.__timber: TimberInterface = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

    async def isToxicSuperTriviaQuestion(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if not await self.__triviaSettingsRepository.areToxicTriviasEnabled():
            return False        

        probability = await self.__triviaSettingsRepository.getToxicProbability()
        return random.uniform(0, 1) <= probability

    async def toxicTriviaWin(
        self,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        result = await self.__toxicTriviaOccurencesRepository.incrementToxicCount(
            twitchChannel = twitchChannel,
            userId = userId
        )

        self.__timber.log('ToxicTriviaHelper', f'In {twitchChannel}, {userName}:{result.getUserId()} won a toxic trivia question!')
