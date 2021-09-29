from packaging.version import parse
from datetime import datetime
from pathlib import Path

"""
Constants that are used almost everywhere in program, these are expected not to change during runtime and
    should be changed manually from the file to achieve desired effect.
    
    TODO: GlobalLaunchParams should be replaced by an argparser
"""

launchtime = datetime.now()
execDateTime = launchtime.strftime("%d-%m-%Y_%H-%M")

GlobalLaunchParams = {
    "GUI": {
        "openEditor": False
    }
}

baseLoc = Path(__file__).parent

OverridesFolder = baseLoc.joinpath("Overrides")
Overrides = []

# Can be replaced by:
#       logFolder = Path("C:\\whatever\\path\\where\\you_store_logs") or Path("/home/ur_user/forPermissionReasons/logsFolder")
logFolder = baseLoc.joinpath("logs")
logFile = logFolder.absolute().joinpath(f"templater-{execDateTime}.log")
logFormat = "[%(asctime)s] %(levelname)s - %(module)s:  %(message)s"

ProgramVersion = parse("0.3.2")

tab = "\t"

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
