from abc import ABC, abstractmethod

try:
    from CynanBotCommon.tts.ttsEvent import TtsEvent
except:
    from tts.ttsEvent import TtsEvent


class TtsManagerInterface(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def submitTtsEvent(self, event: TtsEvent):
        pass
