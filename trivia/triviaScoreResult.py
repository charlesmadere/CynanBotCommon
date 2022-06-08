import locale

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaScoreResult():

    def __init__(
        self,
        streak: int,
        superTriviaWins: int,
        totalLosses: int,
        totalWins: int,
        twitchChannel: str,
        userId: str
    ):
        if not utils.isValidNum(streak):
            raise ValueError(f'streak argument is malformed: \"{streak}\"')
        elif not utils.isValidNum(superTriviaWins):
            raise ValueError(f'superTriviaWins argument is malformed: \"{superTriviaWins}\"')
        elif not utils.isValidNum(totalLosses):
            raise ValueError(f'totalLosses argument is malformed: \"{totalLosses}\"')
        elif not utils.isValidNum(totalWins):
            raise ValueError(f'totalWins argument is malformed: \"{totalWins}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        self.__streak: int = streak
        self.__superTriviaWins: int = superTriviaWins
        self.__totalLosses: int = totalLosses
        self.__totalWins: int = totalWins
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId

    def getAbsStreak(self) -> int:
        return abs(self.__streak)

    def getAbsStreakStr(self) -> str:
        return locale.format_string("%d", self.getAbsStreak(), grouping = True)

    def getStreak(self) -> int:
        return self.__streak

    def getStreakStr(self) -> str:
        return locale.format_string("%d", self.__streak, grouping = True)

    def getSuperTriviaWins(self) -> int:
        return self.__superTriviaWins

    def getSuperTriviaWinsStr(self) -> str:
        return locale.format_string("%d", self.__superTriviaWins, grouping = True)

    def getTotal(self) -> int:
        return self.__totalLosses + self.__totalWins

    def getTotalStr(self) -> str:
        return locale.format_string("%d", self.getTotal(), grouping = True)

    def getTotalLosses(self) -> int:
        return self.__totalLosses

    def getTotalLossesStr(self) -> str:
        return locale.format_string("%d", self.__totalLosses, grouping = True)

    def getTotalWins(self) -> int:
        return self.__totalWins

    def getTotalWinsStr(self) -> str:
        return locale.format_string("%d", self.__totalWins, grouping = True)

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getWinPercent(self) -> float:
        total: int = self.getTotal()

        if total == 0:
            return float(0)

        winPercent = float(self.__totalWins) / float(total)

        if winPercent < 0:
            return float(0)
        elif winPercent > 1:
            return float(1)
        else:
            return winPercent

    def getWinPercentStr(self) -> str:
        winPercent = round(self.getWinPercent() * 100, 2)
        return f'{winPercent}%'
