import asyncio
import traceback
from asyncio import CancelledError as AsyncioCancelledError
from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio.subprocess import Process
from typing import ByteString, Optional, Tuple

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

        process: Optional[Process] = None
        outputTuple: Optional[Tuple[ByteString]] = None
        exception: Optional[Exception] = None

        try:
            process = await asyncio.create_subprocess_shell(
                cmd = command,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE
            )

            outputTuple = await asyncio.wait_for(
                fut = process.communicate(),
                timeout = timeoutSeconds
            )
        except (AsyncioCancelledError, Exception) as e:
            exception = e

        if exception is not None:
            if isinstance(exception, AsyncioTimeoutError) or isinstance(exception, TimeoutError):
                if process is not None:
                    process.terminate()

                self.__timber.log('SystemCommandHelper', f'Encountered timeout exception ({timeoutSeconds=}) when attempting to run system command ({command}): {exception}', exception, traceback.format_exc())
            else:
                self.__timber.log('SystemCommandHelper', f'Encountered unknown exception when attempting to run system command ({command}): {exception}', exception, traceback.format_exc())

            return

        outputString: Optional[str] = None

        if outputTuple is not None and len(outputTuple) >= 2:
            outputString = outputTuple[1].decode('utf-8').strip()

        if utils.isValidStr(outputString):
            self.__timber.log('SystemCommandHelper', f'Ran system command ({command}): \"{outputString}\"')
        else:
            self.__timber.log('SystemCommandHelper', f'Ran system command ({command})')
