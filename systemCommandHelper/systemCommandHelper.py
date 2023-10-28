import traceback
from subprocess import check_output
from typing import Optional

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

        exception: Optional[Exception] = None

        try:
            outputBytes = check_output(command, shell = True)
        except Exception as e:
            exception = e

        if exception is not None:
            self.__timber.log('SystemCommandHelper', f'Encountered exception when attempting to run system command ({command}): {exception}', exception, traceback.format_exc())
        elif outputBytes is None:
            self.__timber.log('SystemCommandHelper', f'None was returned when attempting to run system command ({command})')
        else:
            outputString = outputBytes.decode('utf8')
            self.__timber.log('SystemCommandHelper', f'Ran system command ({command}): \"{outputString}\"')
