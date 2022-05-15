import os
import shutil
import sys
from shutil import SameFileError
from typing import List


def findFiles(src) -> List[str]:
    relevantFiles: List[str] = list()

    for root, dirs, files in os.walk(src):
        if '.vscode' in root:
            continue

        filesToAdd: List[str] = list()

        for file in files:
            if file.endswith('.json') or file.endswith('.log') or file.endswith('.old') or file.endswith('.sqlite'):
                filesToAdd.append(os.path.join(root, file))

        if len(filesToAdd) >= 1:
            relevantFiles.extend(filesToAdd)

    return relevantFiles

def copyFiles(targetDirectory: str, fileList: List[str]):
    for file in fileList:
        commonPath = os.path.commonpath([ targetDirectory, file ])
        targetDirectoryFolderName = targetDirectory[len(commonPath):]
        copyDestination = f'{commonPath}{os.path.sep}{targetDirectoryFolderName}'
        os.makedirs(name = copyDestination, exist_ok = True)

        try:
            shutil.copy2(file, copyDestination)
        except SameFileError as e:
            print(f'Encountered crazy copy error with file \"{file}\" in dir \"{copyDestination}\": {e}')

def main():
    args: List[str] = sys.argv[1:]

    if not args or len(args) != 2:
        print('./backupCynanBot.py <src> <dest>')
        sys.exit(1)

    sourceDirectory = os.path.normcase(os.path.normpath(args[0]))
    targetDirectory = os.path.normcase(os.path.normpath(args[1]))
    print(f'Copying from {sourceDirectory} to {targetDirectory}...')

    fileList = findFiles(sourceDirectory)
    copyFiles(targetDirectory, fileList)

    print(f'Finished copying {len(fileList)} file(s) from {sourceDirectory} to {targetDirectory}')

if __name__ == '__main__':
    main()
