from pathlib import Path
from os import scandir

OverridesFolder = Path(__file__).parent.joinpath("Overrides")
Overrides = []
checked = False

def getOverrides():
    if OverridesFolder.exists():
        if checked is False:
            for Override in scandir(OverridesFolder):
                Overrides.append(Override.name)
        return Overrides
    return None