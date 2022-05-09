try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.streamElements.userPointsResult import UserPointsResult
    from CynanBotCommon.streamElements.userRankResult import UserRankResult
except:
    import utils

    from streamElements.userPointsResult import UserPointsResult
    from streamElements.userRankResult import UserRankResult


class IncrementedUserResult():

    def __init__(
        self,
        pointsResult: UserPointsResult,
        rankResult: UserRankResult
    ):
        if pointsResult is None:
            raise ValueError(f'pointsResult argument is malformed: \"{pointsResult}\"')
        elif rankResult is None:
            raise ValueError(f'rankResult argument is malformed: \"{rankResult}\"')

        self.__pointsResult: UserPointsResult = pointsResult
        self.__rankResult: UserRankResult = rankResult

    def getPointsResult(self) -> UserPointsResult:
        return self.__pointsResult

    def getRankResult(self) -> UserRankResult:
        return self.__rankResult
