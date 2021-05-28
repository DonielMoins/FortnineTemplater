# Config I/O Handler.
from json import loads, dumps

from overridesHandler import Path #, Overrides
import objects.profileObj as prof # pylint: disable=import-error

default_loc = Path(__file__).parent.joinpath("config.json")

# Returns Json of config file
# if file doesant exist, create one from hardcoded default
def get_config(loc=default_loc):
    if not Path(loc).exists():
        with open(loc, "w") as config_file:
            if not config_file.readable():
                raise IOError("Config File Not Readable")
            config_file.write(get_default_config())
    else:
        with open(loc, "r") as config_file:
            if not config_file.readable():
                raise IOError("Config File Not Readable")
    return loads(config_file)

# Write Config File from dict
def write_config_file(settings={}, loc=default_loc):
    with open(loc, "w") as config_file:
        if not config_file.writable():
            raise IOError("Config File Not Writable")
        config_file.write(dumps(settings))

def get_profiles(jsonConfig):
    try:
        profiles = []
        for parentobject in jsonConfig:
            if parentobject is "profiles":
                for profilejson in parentobject:
                    profile = prof.Profile(profilejson)
                    profiles.append(profile)
                    return profiles
    # TODO: test and catch correct exceptions
    except Exception as e: 
        print(e)

        
def get_default_config():
    default_config = \
                    {
                        "profiles": [
                                prof.Profile().__dict__
                            ],
                        "IGNORED": {
                                "Profile Comments" : prof.comments()
                            }
                        }
    return default_config

