from abc import ABC, abstractmethod

try:
    from CynanBotCommon.soundPlayerHelper.soundAlert import SoundAlert
except:
    from soundPlayerHelper.soundAlert import SoundAlert


class SoundPlayerHelperInterface(ABC):

    @abstractmethod
    async def play(self, soundAlert: SoundAlert):
        pass
