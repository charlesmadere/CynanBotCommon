import os
import shutil
import sys
from shutil import SameFileError


def find_files(src):
    relevant_files = []
    for root, dirs, files in os.walk(src):
        relevant_files.extend(os.path.join(root, f) for f in files
            if f.endswith(".json") or f.endswith(".sqlite"))

    return relevant_files


def copy_files(dest, file_list):
    for file in file_list:
        dir = os.path.join(dest, os.path.dirname(file))
        os.makedirs(dir, exist_ok = True)

        try:
            shutil.copy2(file, dir)
        except SameFileError as e:
            print(f'Encountered crazy copy error with file \"{file}\" in dir \"{dir}\"')


def main():
    args = sys.argv[1:]

    if not args:
        print("./backupCynanBot.py <src> <dest>")
        sys.exit(1)

    file_list = find_files(args[0])
    copy_files(args[1], file_list)


if __name__ == '__main__':
    main()
