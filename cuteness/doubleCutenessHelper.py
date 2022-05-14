from datetime import timedelta

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timedDict import TimedDict
except:
    import utils
    from timedDict import TimedDict


class DoubleCutenessHelper():

    def __init__(
        self,
        doubleCutenessDuration: timedelta = timedelta(minutes = 1)
    ):
        if doubleCutenessDuration is None:
            raise ValueError(f'doubleCutenessDuration argument is malformed: \"{doubleCutenessDuration}\"')

        self.__times: TimedDict = TimedDict(doubleCutenessDuration)

    def beginDoubleCuteness(self, twitchHandle: str):
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        self.__times.update(twitchHandle.lower())

    def isWithinDoubleCuteness(self, twitchHandle: str) -> bool:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        return not self.__times.isReady(twitchHandle.lower())
