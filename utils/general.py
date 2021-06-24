from doctest import UnexpectedException
from pathlib import Path
from os import scandir

OverridesFolder = Path(__file__).parent.parent.joinpath("Overrides")
Overrides = []
checked = False

def getOverrides():
    if OverridesFolder.exists():
        if checked is False:
            for Override in scandir(OverridesFolder):
                Overrides.append(Override.name)
        return Overrides
    return None



def parseCSV(lines: list[str], newLines=False, strip=True, ignoreWhiteSpaces=False, sep=","):
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
        UnexpectedException: Throws incase lines is None or its len is 0.
    """    
    
    if not lines or len(lines) == 0:
        raise UnexpectedException("Lines cannot be null and cannot have length of 0.")
       
    if newLines:
        for line in lines:
           if "\n" in line:
               newLines.append(line.split("\n"))
           else: 
               newLines.append(line)
    else: newLines = lines
    
    # ResultCSV List
    CsvList = []
    
    for line in newLines:
        paramLine = []
        for param in line.split(","):
            
            # Cleanup time!
            if strip:
                param.strip()
            if ignoreWhiteSpaces:
                param.replace(" ", "")
                
            paramLine.append(param)
        CsvList.append(paramLine)
    
    return CsvList