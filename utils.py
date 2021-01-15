import math
import urllib
from datetime import datetime
from typing import List


def cleanStr(s: str):
    if s is None:
        return ''
    else:
        return s.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').strip()

def formatTime(time):
    if time is None:
        raise ValueError(f'time argument is malformed: \"{time}\"')

    return time.strftime("%A, %b %d, %Y %I:%M%p")

def formatTimeShort(time, includeSeconds: bool = False):
    if time is None:
        raise ValueError(f'time argument is malformed: \"{time}\"')
    elif includeSeconds is None:
        raise ValueError(f'includeSeconds argument is malformed: \"{includeSeconds}\"')

    if includeSeconds:
        return time.strftime("%b %d %I:%M%S%p")
    else:
        return time.strftime("%b %d %I:%M%p")

def getCleanedSplits(s: str):
    splits = list()

    if not isValidStr(s):
        return splits

    words = s.split()

    if splits is None or len(splits) == 0:
        return words

    for split in splits:
        split = cleanStr(split)

        if isValidStr(split):
            words.append(split)

    return words

def getIntFromDict(d: dict, key: str, fallback: int = None):
    if d is None:
        raise ValueError(f'd argument is malformed: \"{d}\"')
    elif not isValidStr(key):
        raise ValueError(f'key argument is malformed: \"{key}\"')

    value = None

    if key in d and d[key] is not None:
        value = d[key]
    elif fallback is not None:
        value = fallback
    else:
        raise KeyError(f'there is no fallback and key \"{key}\" doesn\'t exist in d: \"{d}\"')

    if not isinstance(value, int):
        value = int(value)

    if not isValidNum(value):
        raise ValueError(f'value \"{value}\" for key \"{key}\" is malformed in d: \"{d}\"')

    return value

def getNowTimeText(includeSeconds: bool = False):
    if includeSeconds is None:
        raise ValueError(f'includeSeconds argument is malformed: \"{includeSeconds}\"')

    return formatTimeShort(
        time=datetime.now(),
        includeSeconds=includeSeconds
    )

def getStrFromDict(d: dict, key: str, fallback: str = None, clean: bool = False):
    if d is None:
        raise ValueError(f'd argument is malformed: \"{d}\"')
    elif not isValidStr(key):
        raise ValueError(f'key argument is malformed: \"{key}\"')
    elif clean is None:
        raise ValueError(f'clean argument is malformed: \"{clean}\"')

    value = None

    if key in d and d[key] is not None:
        value = d[key]
    elif fallback is not None:
        value = fallback
    else:
        raise KeyError(f'there is no fallback and key \"{key}\" doesn\'t exist in d: \"{d}\"')

    if not isinstance(value, str):
        value = str(value)

    if clean:
        value = cleanStr(value)

    return value

def hasItems(l: List):
    return l is not None and len(l) >= 1

def isValidNum(n):
    return n is not None and math.isfinite(n)

def isValidStr(s: str):
    return s is not None and len(s) >= 1 and not s.isspace()

def isValidUrl(s: str):
    if not isValidStr(s):
        return False

    parsed = urllib.parse.urlparse(s)
    url = parsed.geturl()

    return isValidStr(url)

def removePreceedingAt(s: str):
    if not isValidStr(s):
        return s
    elif s[0] != '@':
        return s
    else:
        return s[1:len(s)]
