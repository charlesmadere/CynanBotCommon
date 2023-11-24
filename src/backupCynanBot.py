import os
import re
import shutil
import sys
from shutil import SameFileError
from typing import List, Pattern, Set

jsonFileRegex: Pattern = re.compile(r'^\S+\.json\d*$', re.IGNORECASE)
logFileRegex: Pattern = re.compile(r'^\S+\.log\d*$', re.IGNORECASE)
oldFileRegex: Pattern = re.compile(r'^\S+\.old\d*$', re.IGNORECASE)
sqliteFileRegex: Pattern = re.compile(r'^\S+\.sqlite\d*$', re.IGNORECASE)
allRegex: List[Pattern] = [ jsonFileRegex, logFileRegex, oldFileRegex, sqliteFileRegex ]

def __findFiles(src: str) -> List[str]:
    relevantFiles: List[str] = list()

    for root, dirs, files in os.walk(src):
        if '.vscode' in root:
            continue

        filesToAdd: Set[str] = set()

        for file in files:
            for regex in allRegex:
                if regex.fullmatch(file) is not None:
                    filesToAdd.add(os.path.join(root, file))

        if len(filesToAdd) >= 1:
            relevantFiles.extend(filesToAdd)

    return relevantFiles

def __copyFiles(sourceDirectory: str, targetDirectory: str, fileList: List[str]):
    for file in fileList:
        lastSlashIndex = file.rfind('/')
        withinProjectPath = ''

        if lastSlashIndex != -1:
            withinProjectPath = file[len(sourceDirectory):lastSlashIndex]

        targetDirectoryCommonPath = os.path.commonpath([ targetDirectory, file ])
        targetDirectoryName = targetDirectory[len(targetDirectoryCommonPath):]
        finalCopyDestination = f'{targetDirectoryCommonPath}{os.path.sep}{targetDirectoryName}{os.path.sep}{withinProjectPath}'
        finalCopyDestination = os.path.normcase(os.path.normpath(finalCopyDestination))
        os.makedirs(name = finalCopyDestination, exist_ok = True)

        try:
            shutil.copy2(file, finalCopyDestination)
        except SameFileError as e:
            print(f'Encountered crazy copy error with file \"{file}\" in dir \"{finalCopyDestination}\": {e}')

def performBackup(sourceDirectory: str, targetDirectory: str):
    sourceDirectory = os.path.normcase(os.path.normpath(sourceDirectory))
    targetDirectory = os.path.normcase(os.path.normpath(targetDirectory))
    print(f'Copying from {sourceDirectory} to {targetDirectory}...')

    fileList = __findFiles(sourceDirectory)
    __copyFiles(sourceDirectory, targetDirectory, fileList)

    print(f'Finished copying {len(fileList)} file(s) from {sourceDirectory} to {targetDirectory}')

def main():
    args: List[str] = sys.argv[1:]

    if not args or len(args) != 2:
        print('./backupCynanBot.py <src> <dest>')
        sys.exit(1)

    performBackup(args[0], args[1])

if __name__ == '__main__':
    main()
