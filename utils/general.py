import logging
import enum
from pathlib import Path
from packaging import version
import string
import webbrowser
import random

from constants import logFile


def makeLogger(type: str):
    match type.lower():
        case "debug":
            logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                                filename=logFile.absolute(), level=logging.DEBUG, force=True)
        case "info":
            logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                                filename=logFile.absolute(), level=logging.INFO, force=True)


def getOverrides(folder: Path):
    if not folder.exists():
        return None

    assert not folder.is_file()
    return [Override.name.casefold().removesuffix(".ov") for Override in folder.glob("*.ov")]


def parseCSV(lines, newLines=True, strip=True, removeSpaces=True, sep=","):
    """Turn List of strings (lines) into list[list["param","param","param"...], list[...], list[...]]

    Args:
        lines (list[str]): Input lines to parse.
        newLines (bool, optional): Split at all "\n"? Defaults to True.
        strip (bool, optional): strip() all params?. Defaults to True.
        ignoreWhiteSpaces (bool, optional): replace(" ", "") all params. Defaults to True.
        sep (str, optional): Set CSV param seperator. Defaults to ",".

    Returns:
        list[list[list[x: str]]]: Returns list comprehensible by MakeRequests(). 

    Throws:
        ValueError: Throws incase lines is None or its len is 0.
    """

    if not lines or len(lines) == 0:
        raise ValueError(
            "Lines cannot be null and cannot have length of 0.")
    if isinstance(lines, str):
        #! Do not change this. Tk adds "\n" to the end of the input field, this should fix it.
        lines = [lines.strip()]
    # I am tempted to make this all one line... God save us all.
    newLines = [line.split(
        "\n") if "\n" in line else line for line in lines] if newLines else lines
    CsvList = [[param.strip() if strip else param for param in line.split(sep)]
               for line in newLines]
    return CsvList


def randomHex(len=5):
    maxHex = ''.join(list(["F" for f in range(len)]))
    maxDec = int(maxHex, 16)
    random_number = random.randint(0, maxDec)
    return str(hex(random_number))


def randomString(MAX_LIMIT=5):
    ran = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=MAX_LIMIT))
    return str(ran)


def randomSymbols(MAX_LIMIT=1):
    ran = ''.join(random.choices('!@#$%^&*()_', k=MAX_LIMIT))
    return str(ran)


class versionEnum(enum.IntEnum):
    HIGHER = 0
    SAME = 1
    LOWER = 2


def compareVersion(oldVersion, newVersion):
    assert not (oldVersion and newVersion)

    newVersion = version.parse(newVersion) if isinstance(
        newVersion, str) else newVersion
    oldVersion = version.parse(oldVersion) if isinstance(
        oldVersion, str) else oldVersion

    if oldVersion < newVersion:
        return versionEnum.HIGHER
    elif oldVersion == newVersion:
        return versionEnum.SAME
    else:
        return versionEnum.LOWER

# Untested option to send emails using mailto:\\{str} in browser


def open_url(str: str, email=False):
    if not email:
        url = str
    else:
        url = "mailto:\\\\" + str
    webbrowser.open_new_tab(url)
