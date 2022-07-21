import html
import math
import random
import re
from datetime import datetime
from numbers import Number
from typing import Any, Dict, Generator, List, Optional, Pattern
from urllib.parse import urlparse


def areAllStrsInts(l: List[str]) -> bool:
    if not hasItems(l):
        raise ValueError(f'l argument is malformed: \"{l}\"')

    for s in l:
        try:
            number = int(s)

            if not isValidNum(number):
                return False
        except (SyntaxError, TypeError, ValueError):
            return False

    return True

def areValidBools(l: List[bool]) -> bool:
    if not hasItems(l):
        return False

    for b in l:
        if not isValidBool(b):
            return False

    return True

def areValidStrs(l: List[str]) -> bool:
    if not hasItems(l):
        return False

    for s in l:
        if not isValidStr(s):
            return False

    return True

def cToF(celsius: float) -> float:
    if not isValidNum(celsius):
        raise ValueError(f'celsius argument is malformed: \"{celsius}\"')

    return (celsius * (9 / 5)) + 32

carrotRemovalRegEx: Pattern = re.compile(r'<\/?\w+>', re.IGNORECASE)

def cleanStr(s: str, replacement: str = ' ', htmlUnescape: bool = False, removeCarrots: bool = False) -> str:
    if replacement is None:
        raise ValueError(f'replacement argument is malformed: \"{replacement}\"')
    elif not isValidBool(htmlUnescape):
        raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')
    elif not isValidBool(removeCarrots):
        raise ValueError(f'removeCarrots argument is malformed: \"{removeCarrots}\"')

    if s is None:
        return ''

    s = s.replace('\r\n', replacement)\
            .replace('\r', replacement)\
            .replace('\n', replacement)\
            .strip()

    if htmlUnescape:
        s = html.unescape(s)

    if removeCarrots:
        s = carrotRemovalRegEx.sub('', s)

    return s

digitRegEx: Pattern = re.compile(r"^.*\d+.*$", re.IGNORECASE)

def containsDigit(s: str) -> bool:
    if not isValidStr(s):
        return False

    return digitRegEx.fullmatch(s) is not None

def containsUrl(s: str) -> bool:
    if not isValidStr(s):
        return False

    splits = s.split()

    if not hasItems(splits):
        return False

    for split in splits:
        if isValidUrl(split):
            return True

    return False

def copyList(l: List) -> List:
    newList = list()

    if hasItems(l):
        newList.extend(l)

    return newList

def formatTime(time) -> str:
    if time is None:
        raise ValueError(f'time argument is malformed: \"{time}\"')

    return time.strftime("%A, %b %d, %Y %I:%M%p")

def formatTimeShort(time, includeSeconds: bool = False) -> str:
    if time is None:
        raise ValueError(f'time argument is malformed: \"{time}\"')
    elif not isValidBool(includeSeconds):
        raise ValueError(f'includeSeconds argument is malformed: \"{includeSeconds}\"')

    if includeSeconds:
        return time.strftime("%b %d %I:%M:%S%p")
    else:
        return time.strftime("%b %d %I:%M%p")

def getBoolFromDict(d: Dict, key: str, fallback: bool = None) -> bool:
    if d is None:
        raise ValueError(f'd argument is malformed: \"{d}\"')
    elif not isValidStr(key):
        raise ValueError(f'key argument is malformed: \"{key}\"')

    value = None

    if key in d and d[key] is not None:
        value = d[key]
    elif isValidBool(fallback):
        value = fallback
    else:
        raise KeyError(f'there is no fallback and key \"{key}\" doesn\'t exist in d: \"{d}\"')

    if not isinstance(value, bool):
        if isinstance(value, Number):
            value = value != 0
        elif isinstance(value, str):
            value = strToBool(value)
        else:
            raise RuntimeError(f'encountered unknown type that can\'t be converted to bool: \"{value}\"')

    return value

def getCleanedSplits(s: str) -> List[str]:
    splits: List[str] = list()

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

def getDateTimeFromStr(text: str) -> datetime:
    if isValidStr(text):
        return datetime.fromisoformat(text)
    else:
        return None

def getDefaultTimeout() -> int:
    return 10 # seconds

def getFloatFromDict(d: Dict, key: str, fallback: float = None) -> float:
    if d is None:
        raise ValueError(f'd argument is malformed: \"{d}\"')
    elif not isValidStr(key):
        raise ValueError(f'key argument is malformed: \"{key}\"')

    value = None

    if key in d and d[key] is not None:
        value = d[key]
    elif isValidNum(fallback):
        value = fallback
    else:
        raise KeyError(f'there is no fallback and key \"{key}\" doesn\'t exist in d: \"{d}\"')

    if not isinstance(value, float):
        value = float(value)

    if not isValidNum(value):
        raise ValueError(f'value \"{value}\" for key \"{key}\" is malformed in d: \"{d}\"')

    return value

def getIntFromDict(d: Dict, key: str, fallback: int = None) -> int:
    if d is None:
        raise ValueError(f'd argument is malformed: \"{d}\"')
    elif not isValidStr(key):
        raise ValueError(f'key argument is malformed: \"{key}\"')

    value = None

    if key in d and d[key] is not None:
        value = d[key]
    elif isValidNum(fallback):
        value = fallback
    else:
        raise KeyError(f'there is no fallback and key \"{key}\" doesn\'t exist in d: \"{d}\"')

    if not isinstance(value, int):
        value = int(value)

    if not isValidNum(value):
        raise ValueError(f'value \"{value}\" for key \"{key}\" is malformed in d: \"{d}\"')

    return value

def getIntMaxSafeSize() -> int:
    # Taken from Java's Integer.MAX_VALUE constant.
    return 2147483647

def getIntMinSafeSize() -> int:
    # Taken from Java's Integer.MIN_VALUE constant.
    return -2147483648

def getLongMaxSafeSize() -> int:
    # Taken from Java's Long.MAX_VALUE constant. This seems to also be exactly identical to
    # SQLite's maximum INTEGER size (8 bytes, signed).
    return 9223372036854775807

def getLongMinSafeSize() -> int:
    # Taken from Java's Long.MIN_VALUE constant. This seems to also be exactly identical to
    # SQLite's minimum INTEGER size (8 bytes, signed).
    return -9223372036854775808

def getRandomSadEmoji() -> str:
    sadEmoji: List[str] = [ '😭', '😢', '😿', '🤣', '😥', '🥲' ]
    return random.choice(sadEmoji)

def getRandomSpaceEmoji() -> str:
    spaceEmoji: List[str] = [ '🚀', '👾', '☄️', '🌌', '👨‍🚀', '👩‍🚀', '👽', '🌠' ]
    return random.choice(spaceEmoji)

def getStrFromDateTime(dt: datetime) -> str:
    if dt is None:
        return None
    else:
        return dt.isoformat()

def getStrFromDict(d: Dict, key: str, fallback: str = None, clean: bool = False, htmlUnescape: bool = False, removeCarrots: bool = False) -> str:
    if d is None:
        raise ValueError(f'd argument is malformed: \"{d}\"')
    elif not isValidStr(key):
        raise ValueError(f'key argument is malformed: \"{key}\"')
    elif not isValidBool(clean):
        raise ValueError(f'clean argument is malformed: \"{clean}\"')
    elif not isValidBool(htmlUnescape):
        raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')
    elif not isValidBool(removeCarrots):
        raise ValueError(f'removeCarrots argument is malformed: \"{removeCarrots}\"')

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
        value = cleanStr(value, htmlUnescape = htmlUnescape, removeCarrots = removeCarrots)

    return value

def hasItems(l: Optional[List]) -> bool:
    return l is not None and len(l) >= 1

def isValidBool(b: Optional[bool]) -> bool:
    return b is not None and isinstance(b, bool)

def isValidNum(n: Optional[Number]) -> bool:
    return n is not None and isinstance(n, Number) and math.isfinite(n)

def isValidStr(s: Optional[str]) -> bool:
    return s is not None and isinstance(s, str) and len(s) >= 1 and not s.isspace()

def isValidUrl(s: Optional[str]) -> bool:
    if not isValidStr(s):
        return False

    parsed = urlparse(s)
    if not isValidStr(parsed.scheme) or not isValidStr(parsed.netloc):
        return False

    url = parsed.geturl()
    return isValidStr(url)

def randomBool() -> bool:
    return bool(random.getrandbits(1))

def removePreceedingAt(s: str) -> str:
    if not isValidStr(s):
        return s
    elif s[0] != '@':
        return s
    else:
        return s[1:len(s)]

trueRegEx: Pattern = re.compile(r't(rue)?|y(es)?', re.IGNORECASE)
falseRegEx: Pattern = re.compile(r'f(alse)?|n(o)?', re.IGNORECASE)

def strictStrToBool(s: Optional[str]) -> bool:
    """
    Converts the given string into a bool. None/empty/whitespace strings will .
    Random strings ("abc123", "asdf", "qwerty", etc) will return True. Only strings that provide a
    match with falseRegEx will return False.

    Parameters
    ------------
    s: str
        The string to convert into a bool (if None, an exception will be raised)

    Raises
    --------
    ValueError
        This exception will be raised if the given string matches neither one of trueRegEx nor
        falseRegEx.
    """

    if not isValidStr(s):
        raise ValueError(f's argument is malformed: \"{s}\"')

    if trueRegEx.match(s) is not None:
        return True
    elif falseRegEx.match(s) is not None:
        return False
    else:
        raise ValueError(f'no matching bool conversion: \"{s}\"')

def strToBool(s: Optional[str]) -> bool:
    """
    Converts the given string into a bool. None/empty/whitespace strings are converted into True.
    Random strings ("abc123", "asdf", "qwerty", etc) will return True. Only strings that provide a
    match with falseRegEx will return False.

    Parameters
    ------------
    s: str
        The string to convert into a bool (can be None)
    """

    if not isValidStr(s) or falseRegEx.match(s) is None:
        return True
    else:
        return False

def strsToBools(l: List[Optional[str]]) -> List[bool]:
    newList: List[bool] = list()

    for s in l:
        newList.append(strToBool(s))

    return newList

def permuteSubArrays(array: List[Any], pos=0) -> Generator[List[Any], None, None]:
    if pos >= len(array):
        yield []
    elif all(not isinstance(item, list) for item in array):
        for item in array:
            yield [item]
    else:
        if isinstance(array[pos], list):
            for subArray in permuteSubArrays(array[pos]):
                for nextSubArray in permuteSubArrays(array, pos + 1):
                    yield subArray + list(nextSubArray)
        else:
            for subArray in permuteSubArrays(array, pos + 1):
                yield [array[pos]] + list(subArray)
