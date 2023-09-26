from abc import abstractmethod

try:
    from CynanBotCommon.clearable import Clearable
except:
    from clearable import Clearable


class ChatBandManagerInterface(Clearable):

    @abstractmethod
    async def playInstrumentForMessage(self, twitchChannel: str, author: str, message: str) -> bool:
        pass
