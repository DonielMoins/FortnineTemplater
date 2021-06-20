# Config I/O Handler.
import inspect
from types import MappingProxyType
from typing import Optional
import hjson
import pickle
import logging
from hjson import loads, HjsonEncoder, load, HjsonDecodeError
from pathlib import Path 

from classes import profileObj as prof, requestObj

# TODO: Make settings file window.
default_loc = Path(__file__).parent.parent.joinpath("config.hjson")

def dumps(obj, **kwargs):
    return hjson.dumps(obj, cls=_ConfigEncoder, indent=4)

# Returns Json of config file
# if file doesant exist, create one from hardcoded default
def get_config(loc=default_loc):
    hjsonO = ""
    configlines = ""
    try:
        if not Path(loc).exists():
            configlines = write_config_file(loc=loc)
        
        with open(loc, "r") as config_file:
            if not config_file.readable():
                logging.error("Config File Not Readable")
                raise IOError("Config File Not Readable")
            
            hjsonO = load(config_file)
            if len(hjsonO) == 0:
                logging.error("Config HJSon Object Empty")
                raise HjsonDecodeError("Config HJSon Object Empty", config_file.readline(), 0)
            hjsonO.__delitem__("IGNORED")
            return hjsonO
    except HjsonDecodeError as error:
        if len(configlines) < 10 or len(hjsonO) == 0:
            logging.warning("Config file is likely malformed, remaking config.")
            backup_config(loc)
            write_config_file(build_config(), loc=loc)
        else:
            logging.error(error)
        
            
# Using Optional cause 
def write_config_file(settings=Optional[list], loc=default_loc):
    """Function to write config file

    Args:
        settings (dict, optional): Dictionary of all settings to write to file. Defaults to build_config() if None is provided.
        loc ([type], optional): [description]. Defaults to default_loc.

    Raises:
        IOError: Config not writable.

    Returns:
        str: return config string
    """    
    if len(settings) < 1:
        settings = build_config()

    with open(loc, "w") as config_file:
        if not config_file.writable():
            raise IOError("Config File Not Writable")
        configstr = dumps(settings)
        config_file.write(configstr)
        return configstr
        
def backup_config(oldloc=default_loc, retry=True):
    
    def recursivebackuploc(oldloc):
        newloc = oldloc.__str__() + ".bak"
        if Path(newloc).exists():
            return recursivebackuploc(newloc)
        else: 
            return newloc
        
    old_data = ""
    if Path(oldloc.__str__() + ".bak").exists():
        if retry:
            backuploc = recursivebackuploc(oldloc)
        else:
            raise FileExistsError("Config.yml already exists and retry mode is disabled")
    else:
        backuploc = Path(oldloc.__str__() + ".bak")
        
    with open(oldloc, "r") as old_file:
        old_data = old_file.readlines()
        
    with open(backuploc, "w") as backup_file:
        if backup_file.writable():
            backup_file.writelines(old_data)
        else:
            print("Could not safely write backup config file!")
            raise IOError("Could not safely write backup config file! \n File not writable, check Folder permissions!")

def get_profiles(jsonConfig):
    try:
        # TODO: FIX THIS MESSSSSSS
        profiles = []
        for parentobject in jsonConfig:
            if parentobject == "profiles":
                for profileItem in jsonConfig["profiles"]:
                    profileDict = profileItem["Profile"]
                    profile = prof.Profile(settings=profileDict) 
                    profiles.append(profile)
                    return profiles
    # TODO: test and catch correct exceptions
    except Exception as error: # pylint: disable=broad-except
        print(error)

        
def build_config():
    default_config = {
                    "profiles": [prof.Profile()],
                    # "IGNORED": {"Profile Comments" : prof.comments()}
                    "IGNORED": {}
                    }
    return default_config

class _ConfigEncoder(HjsonEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return HjsonEncoder.default(self, obj)
        if isinstance(obj, MappingProxyType):
            return dict(obj)
        if isinstance(obj, type(list[requestObj.Request])):
            for i in obj.__iter__:
                self.default(self, i)
        if type(obj) is requestObj.Request or prof.Profile:
            return {type(obj).__name__: obj.__dict__}
        return {"_unknown_object": pickle.dumps(obj)}


# TODO: Fix this garbage code
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