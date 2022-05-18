from datetime import timedelta

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timedDict import TimedDict
except:
    import utils
    from timedDict import TimedDict


class SuperTriviaHelper():

    def __init__(
        self,
        superTriviaCooldown: timedelta = timedelta(minutes = 2, seconds = 30)
    ):
        if superTriviaCooldown is None:
            raise ValueError(f'superTriviaCooldown argument is malformed: \"{superTriviaCooldown}\"')

        self.__times: TimedDict = TimedDict(superTriviaCooldown)

    def startSuperTrivia(self, twitchHandle: str) -> bool:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        return self.__times.isReadyAndUpdate(twitchHandle.lower())
