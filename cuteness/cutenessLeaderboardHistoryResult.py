from typing import List, Optional

try:
    import CynanBotCommon.utils as utils

    from CynanBotCommon.cuteness.cutenessLeaderboardResult import CutenessLeaderboardResult
except:
    import utils

    from cuteness.cutenessLeaderboardResult import CutenessLeaderboardResult


class CutenessLeaderboardHistoryResult():

    def __init__(
        self,
        twitchChannel: str,
        leaderboards: Optional[List[CutenessLeaderboardResult]] = None
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__twitchChannel: str = twitchChannel
        self.__leaderboards: List[CutenessLeaderboardResult] = leaderboards

    def getLeaderboards(self) -> List[CutenessLeaderboardResult]:
        return self.__leaderboards

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def hasLeaderboards(self) -> bool:
        return utils.hasItems(self.__leaderboards)
