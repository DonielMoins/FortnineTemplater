from pathlib import Path
from os import scandir

OverridesFolder = Path(__file__, "Overrides")
Overrides = []

if OverridesFolder.exists():
    for Override in scandir(OverridesFolder):
        Overrides.append(Override.name)