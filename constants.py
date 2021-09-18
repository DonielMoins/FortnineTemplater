from datetime import date
from pathlib import Path
from packaging.version import parse

"""
Constants that are used almost everywhere in program, these are expected not to change during runtime and
    should be changed manually from the file to achieve desired effect.
    
    TODO: GlobalLaunchParams should be replaced by an argparser
"""

today = date.today()
dayDate = today.strftime("%d-%m-%Y")

GlobalLaunchParams = {
    "GUI": {
        "openEditor": False
    }
}

OverridesFolder = Path(__file__).parent.joinpath("Overrides")
Overrides = []

# Can be replaced by:
#       logFolder = Path("C:\\whatever\\path\\where\\you_store_logs") or Path("/home/ur_user/forPermissionReasons/logsFolder")
logFolder = Path(__file__).parent.joinpath("logs")
logFile = logFolder.absolute().joinpath(f"templater-{dayDate}.log")


ProgramVersion = parse("0.3.0")

ProjDetails = {
    "github": "https://github.com/DonielMoins/FortnineTemplater/",
    "version": str(ProgramVersion)
}
DevDetails = [
    {
        "name": "Fakhri Hammami",
        "username": "DonielMoins",
        "github": "https://github.com/DonielMoins/",
        "email": "Fakhri.Hamm@gmail.com"
    },

]
