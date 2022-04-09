import os

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberEntry import TimberEntry
except:
    import utils

    from timber.timberEntry import TimberEntry


class Timber():

    def __init__(
        self,
        alsoPrintToStandardOut: bool = True,
        timberRootDirectory: str = 'CynanBotCommon/timber'
    ):
        if not utils.isValidBool(alsoPrintToStandardOut):
            raise ValueError(f'alsoPrintToStandardOut argument is malformed: \"{alsoPrintToStandardOut}\"')
        elif not utils.isValidStr(timberRootDirectory):
            raise ValueError(f'timberRootDirectory argument is malformed: \"{timberRootDirectory}\"')

        self.__alsoPrintToStandardOut: bool = alsoPrintToStandardOut
        self.__timberRootDirectory: str = timberRootDirectory

    def __getLogStatement(
        self,
        ensureNewLine: bool,
        timberEntry: TimberEntry
    ) -> str:
        if not utils.isValidBool(ensureNewLine):
            raise ValueError(f'ensureNewLine argument is malformed: \"{ensureNewLine}\"')
        elif timberEntry is None:
            raise ValueError(f'timberEntry argument is malformed: \"{timberEntry}\"')

        logStatement = f'{timberEntry.getSimpleDateTime().getDateAndTimeStr()} — {timberEntry.getTag()} — {timberEntry.getMsg()}'
        logStatement.strip()

        if ensureNewLine:
            logStatement = f'{logStatement}\n'

        return logStatement

    def log(self, tag: str, msg: str):
        if not utils.isValidStr(tag):
            raise ValueError(f'tag argument is malformed: \"{tag}\"')
        elif not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')

        timberEntry = TimberEntry(tag, msg)
        self.__writeToLogFile(timberEntry)

        if self.__alsoPrintToStandardOut:
            print(self.__getLogStatement(False, timberEntry))

    def __writeToLogFile(self, timberEntry: TimberEntry):
        if timberEntry is None:
            raise ValueError(f'timberEntry argument is malformed: \"{timberEntry}\"')

        sdt = timberEntry.getSimpleDateTime()
        timberDirectory = f'{self.__timberRootDirectory}/{sdt.getYearStr()}/{sdt.getMonthStr()}'
        timberFile = f'{timberDirectory}/{sdt.getDayStr()}.log'

        if not os.path.exists(timberDirectory):
            os.makedirs(timberDirectory)

        logStatement = self.__getLogStatement(True, timberEntry)

        with open(timberFile, 'a') as file:
            file.write(logStatement)
