try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.tts.ttsManagerInterface import TtsManagerInterface
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from CynanBotCommon.users.userInterface import UserInterface
except:
    import utils
    from systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from timber.timberInterface import TimberInterface
    from tts.ttsManagerInterface import TtsManagerInterface
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface

    from users.userInterface import UserInterface


class TtsManager(TtsManagerInterface):

    def __init__(
        self,
        systemCommandHelper: SystemCommandHelperInterface,
        timber: TimberInterface,
        ttsSettingsRepository: TtsSettingsRepositoryInterface
    ):
        if not isinstance(systemCommandHelper, SystemCommandHelperInterface):
            raise ValueError(f'systemCommandHelper argument is malformed: \"{systemCommandHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(ttsSettingsRepository, TtsSettingsRepositoryInterface):
            raise ValueError(f'ttsSettingsRepository argument is malformed: \"{ttsSettingsRepository}\"')

        self.__systemCommandHelper: SystemCommandHelperInterface = systemCommandHelper
        self.__timber: TimberInterface = timber
        self.__ttsSettingsRepository: TtsSettingsRepositoryInterface = ttsSettingsRepository

    async def executeTts(self, user: UserInterface, message: str):
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        # TODO
        pass
