import asyncio
import traceback
from typing import ByteString, Optional

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

    def __init__(self, timber: TimberInterface):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: TimberInterface = timber

    async def executeCommand(self, command: str, timeoutSeconds: float = 10):
        if not utils.isValidStr(command):
            self.__timber.log('SystemCommandHelper', f'Received malformed command argument: \"{command}\"')
            return
        elif not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 3 or timeoutSeconds > utils.getIntMaxSafeSize():
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        outputBytes: Optional[ByteString] = None
        exception: Optional[Exception] = None

        try:
            proc = await asyncio.create_subprocess_shell(
                cmd = command,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE
            )

            outputBytes = await asyncio.wait_for(
                fut = proc.communicate(),
                timeout = timeoutSeconds
            )
        except TimeoutError as e:
            exception = e
        except Exception as e:
            exception = e

        # try:
        #     outputBytes = check_output(command, shell = True)
        # except Exception as e:
        #     exception = e

        if exception is not None:
            self.__timber.log('SystemCommandHelper', f'Encountered exception when attempting to run system command ({command}): {exception}', exception, traceback.format_exc())
            return

        outputString: Optional[str] = None

        if outputBytes is not None:
            outputString = outputBytes.decode('utf-8')

        if utils.isValidStr(outputString):
            self.__timber.log('SystemCommandHelper', f'Ran system command ({command}): \"{outputString}\"')
        else:
            self.__timber.log('SystemCommandHelper', f'Ran system command ({command})')
