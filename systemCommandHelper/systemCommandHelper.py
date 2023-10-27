try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from timber.timberInterface import TimberInterface


class SystemCommandHelper(SystemCommandHelperInterface):

    def __self__(self, timber: TimberInterface):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: TimberInterface = timber

    async def executeCommand(self, command: str):
        if not utils.isValidStr(command):
            self.__timber.log('SystemCommandHelper', f'Received malformed command argument: \"{command}\"')
            return

        # TODO
        pass
