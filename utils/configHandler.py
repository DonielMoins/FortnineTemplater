# Config I/O Handler.
import inspect
import json
import pickle
import logging
from json import loads, JSONEncoder, load
from json.decoder import JSONDecodeError as JSONDecodeError
from pathlib import Path 

from objects import profileObj as prof

default_loc = Path(__file__).parent.parent.joinpath("config.json")

def dumps(obj, **kwargs):
    return json.dumps(obj, cls=_TemplateObjectEncoder, indent=4)

# Returns Json of config file
# if file doesant exist, create one from hardcoded default
def get_config(loc=default_loc):
    try:
        if not Path(loc).exists():
            configlines = write_config_file(loc=loc)
        
        with open(loc, "r") as config_file:
            if not config_file.readable():
                raise IOError("Config File Not Readable")
            return load(config_file)
    except JSONDecodeError as error:
        if len(configlines) < 10:
            logging.warning("Config file is likely invalid, remaking config.")
            backup_config(loc)
            write_config_file(build_config(), loc=loc)
        logging.ERROR(repr(error))
            

# Write Config File from dict
def write_config_file(settings={}, loc=default_loc):
    if len(settings) < 1:
        settings = build_config()

    with open(loc, "w") as config_file:
        if not config_file.writable():
            raise IOError("Config File Not Writable")
        configstr = dumps(settings)
        config_file.write(configstr)
        return configstr
        
def backup_config(loc=default_loc, retry=True):
    
    def recursivebackuploc(oldloc):
        newloc = oldloc.__str__() + ".bak"
        if Path(newloc).exists():
            return recursivebackuploc(newloc)
        else: 
            return newloc
        
    old_data = ""
    if Path(oldloc.__str__() + ".bak").exists():
        if retry:
            backuploc = recursivebackuploc(loc)
        else:
            raise FileExistsError("Config.yml already exists and retry mode is disabled")
    else:
        backuploc = Path(oldloc.__str__() + ".bak")
        
    with open(loc, "r") as old_file:
        old_data = old_file.readlines()
    with open(backuploc, "w") as backup_file:
        if backup_file.writable():
            backup_file.writelines(old_data)
        else:
            print("Could not safely write backup config file!")
            raise IOError("Could not safely write backup config file! \n File not writable, check Folder permissions!")

def get_profiles(jsonConfig):
    try:
        profiles = []
        for parentobject in jsonConfig:
            if parentobject == "profiles":
                for profilejson in parentobject:
                    profile = prof.Profile(profilejson) 
                    profiles.append(profile)
                    return profiles
    # TODO: test and catch correct exceptions
    except Exception as error: # pylint: disable=broad-except
        print(error)

        
def build_config():
    default_config = {
                    "profiles": [prof.Profile()],
                    "IGNORED": {"Profile Comments" : prof.comments()}
                    }
    return default_config

class _TemplateObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        if inspect.isclass(obj) or inspect.isclass(type(obj)):
            return {type(obj).__name__: obj.__dict__}
        return {"_unknown_object": pickle.dumps(obj)}


# TODO Fix this garbage code
# def DictToLines (Dict: dict, recursive=True):
#     if len(Dict) > 0: 
#         if isinstance(Dict, list):
#             return Dict 
#         elif isinstance(Dict, dict):
#             Dict = Dict.items()  
#     else: 
#         return []
#     List = []
#     for item in Dict:
#         if isinstance(item, dict):
#             List.append(DictToLines(item)) if recursive else str(item)
#         else: List.append(str(item))
#     return List