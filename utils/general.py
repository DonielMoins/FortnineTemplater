from constants import logFile, logFolder
from threading import current_thread
from constants import logFormat
from packaging import version
from pathlib import Path
from typing import List

import webbrowser
import logging
import random
import string
import enum

# Check/make logs folder, then


def makeLogger(type: str = "", name = current_thread().name):

    if not logFolder.exists():
        try:
            logFolder.mkdir()
        except Exception as e:
            logging.exception(e)
            print(e.with_traceback())

    if type.lower() == "debug":
            lvl = logging.DEBUG
    if type.lower() == "info":
            lvl = logging.INFO
    else:
            lvl = logging.NOTSET

    logging.basicConfig(format = logFormat, 
                        filename = logFile.absolute(), level = lvl, force = True)
    formatter = logging.Formatter(
        logFormat)
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    ch.setLevel(logger.level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def getOverrides(folder: Path):
    if not folder.exists():
        return None

    assert not folder.is_file()
    return [Override.name.casefold().removesuffix(".ov") for Override in folder.glob("*.ov")]


def parseCSV(lines, newLines = True, strip = True, removeSpaces = True, sep = ","):
    """Turn List of strings (lines) into list[list["param", "param", "param"...], list[...], list[...]]

    Args:
        lines (list[str]): Input lines to parse.
        newLines (bool, optional): Split at all "\n"? Defaults to True.
        strip (bool, optional): strip() all params?. Defaults to True.
        ignoreWhiteSpaces (bool, optional): replace(" ", "") all params. Defaults to True.
        sep (str, optional): Set CSV param seperator. Defaults to ", ".

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


def randomHex(len = 5):
    maxHex = ''.join(list(["F" for f in range(len)]))
    maxDec = int(maxHex, 16)
    random_number = random.randint(0, maxDec)
    return str(hex(random_number))


def randomString(MAX_LIMIT = 5):
    ran = ''.join(random.choices(
        string.ascii_uppercase+ string.digits, k = MAX_LIMIT))
    return str(ran)


def randomSymbols(MAX_LIMIT = 1):
    ran = ''.join(random.choices('!@#$%^&*()_', k = MAX_LIMIT))
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


def open_url(str: str, email = False):
    if not email:
        url = str
    else:
        url = "mailto:\\\\" + str
    webbrowser.open_new_tab(url)


"""
Functions for pretty printing / logging
"""


def basic_multiline_banner(text: str = '', ch: str = "=", width = 120):
    ch = ch.strip()[:1]
    
    char = ch * width
    pad = (width + len(text)) // 2
    return "{cha}\n{banner}\n{cha}".format(cha=char, banner=one_line_banner(text, ch, width))


def one_line_banner(text: str = "", ch: str= '=', width = 120):
    """Creates a one-line string banner using input.
    Ex:
        In:  ('Content End', ch = '-', )
        Out: '----------------------------------------------------- Content End------------------------------------------------------'

    Args:
        text (str): String used for creation of banner
        ch (str, optional): [description]. Defaults to ' = '.
        width (int, optional): [description]. Defaults to 120.

    Returns:
        [type]: [description]
    """
    
    ch = ch.strip()[:1]
    
    spaced_text = f' {text} ' if text else ""
    banner = spaced_text.center(width, ch)
    return banner


def logger_ml(logger: logging.Logger, textLines: List[str], logLevel = logging.INFO):

    if logLevel == logging.INFO:
            def log(text): return logger.info(text)
    if logLevel == logging.DEBUG:
            def log(text): return logger.debug(text)
    if logLevel == logging.WARNING:
            def log(text): return logger.warning(text)
    if logLevel == logging.ERROR:
            def log(text): return logger.info(text)
    else:
        def log(text): return logger.info(text)

    # top + textLines + bottom
    for i in textLines:
            log(i)
