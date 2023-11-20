from abc import abstractmethod

try:
    from CynanBotCommon.cheerActions.cheerActionRemodData import \
        CheerActionRemodData
    from CynanBotCommon.clearable import Clearable
except:
    from cheerActions.cheerActionRemodData import CheerActionRemodData
    from clearable import Clearable


class CheerActionRemodHelperInterface(Clearable):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def submitRemodAction(action: CheerActionRemodData):
        pass
