import enum
from pathlib import Path
from packaging import version
from os import scandir
import string
import webbrowser
import random


def getOverrides(folder: Path):
    items = []
    if folder.exists() and folder.is_dir():
        overrideGen = folder.glob("*.ov")
        for Override in overrideGen:
            items.append(Override.name.removesuffix(".ov").casefold())
        return items
    elif folder.exists():
        return f"File exists en lieu of Overrides Folder.\n Check this location {folder.absolute()}"
    return None


def parseCSV(lines, newLines=True, strip=True, ignoreWhiteSpaces=False, sep=","):
    """Turn List of strings (lines) into list[list["param","param","param"...], list[...], list[...]]

    Args:
        lines (list[str]): Input lines to parse.
        newLines (bool, optional): Split at all "\n"? Defaults to False.
        strip (bool, optional): strip() all params?. Defaults to True.
        ignoreWhiteSpaces (bool, optional): replace(" ", "") all params?. Defaults to False.
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
        # Do not change this. Tk adds \n to the end of the input field, this should fix it.
        lines = [lines.strip()]
    if newLines:
        newLines = []
        for line in lines:
            if "\n" in line:
                newLines = line.split("\n")
            else:
                newLines.append(line)
    else:
        newLines = lines

    # ResultCSV List
    CsvList = []

    for line in newLines:
        paramLine = []
        for param in line.split(sep):

            # Cleanup time!
            if strip:
                param.strip()
            if ignoreWhiteSpaces:
                param.replace(" ", "")

            paramLine.append(param)
        CsvList.append(paramLine)

    return CsvList


def randomHex(len=5):
    maxHex = ''
    for f in range(len):
        maxHex += "F"
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
    if not (oldVersion and newVersion):
        raise ValueError("Invalid version values.")
    if isinstance(newVersion, str) or isinstance(oldVersion, str):
        newVersion = version.parse(newVersion)
        oldVersion = version.parse(oldVersion)
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
