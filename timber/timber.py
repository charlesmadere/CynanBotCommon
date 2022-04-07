import os

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime


class Timber():

    def __init__(
        self,
        alsoLogToStandardOut: bool = True,
        timberRootDirectory: str = 'CynanBotCommon/timber'
    ):
        if not utils.isValidBool(alsoLogToStandardOut):
            raise ValueError(f'alsoLogToStandardOut argument is malformed: \"{alsoLogToStandardOut}\"')
        elif not utils.isValidStr(timberRootDirectory):
            raise ValueError(f'timberRootDirectory argument is malformed: \"{timberRootDirectory}\"')

        self.__alsoLogToStandardOut: bool = alsoLogToStandardOut
        self.__timberRootDirectory: str = timberRootDirectory

    def log(self, tag: str, msg: str):
        if not utils.isValidStr(tag):
            raise ValueError(f'tag argument is malformed: \"{tag}\"')
        elif not utils.isValidStr(msg):
            return

        tag = tag.strip()
        msg = msg.strip()
        now = SimpleDateTime()
        logStatement = f'{now.getDateAndTimeStr()} — {tag} — {msg}'

        self.__writeToLogFile(now, logStatement)

        if self.__alsoLogToStandardOut:
            print(logStatement)

    def __writeToLogFile(self, now: SimpleDateTime, logStatement: str):
        if now is None:
            raise ValueError(f'now argument is malformed: \"{now}\"')
        elif not utils.isValidStr(logStatement):
            raise ValueError(f'logStatement argument is malformed: \"{logStatement}\"')

        timberDirectory = f'{self.__timberRootDirectory}/{now.getYear()}/{now.getMonth()}'
        timberFile = f'{timberDirectory}/{now.getDay()}.log'

        if not os.path.exists(timberDirectory):
            os.makedirs(timberDirectory)

        if logStatement[len(logStatement) - 1] != '\n':
            logStatement = f'{logStatement}\n'

        with open(timberFile, 'a') as file:
            file.write(logStatement)
