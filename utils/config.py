# Config I/O Handler.
import tkinter
from types import MappingProxyType
from typing import Optional
import hjson, logging, os
from hjson import HjsonEncoder, HjsonDecodeError, load 
from pathlib import Path

from packaging import version 
from objects import Profile, Request
from utils.general import ProgramVersion

# TODO: Make settings file window.

    
home_dir = Path(__file__).parent.parent
configPath = home_dir.joinpath("config.hjson")
class BaseConfig:
    def __init__(self, *args, **kwargs):
        self.configVersion = ProgramVersion
        self.profiles = [Profile(), Profile()]
        self.settings = {}
        self._location: Path = configPath
        if kwargs:
            self.__dict__.update(kwargs)
            
    def write_config_file(self, loc: Path = None):
        """Function to write config file
    
        Args:
            settings (dict, optional): Dictionary of all settings to write to file. Defaults to build_config() if None is provided.
            loc ([type], optional): Path of config.hjson file. Defaults to default_loc.
    
        Raises:
            IOError: Config not writable.
    
        Returns:
            str: return config string
        """    
        if loc:
            self._location = loc
        with open(self._location, "w") as config_file:
            if not config_file.writable():
                raise IOError("Config File Not Writable")
            configstr = dumps(self.json())
            config_file.write(configstr)
            return configstr

    
    def json(self):
        json = vars(self)
        itemsToDelete = []
        for key in json.keys():
            if key.startswith("_"):
                itemsToDelete.append(key)
        for key in itemsToDelete:
            json.__delitem__(key)
        return json

def dumps(obj, **kwargs):
    return hjson.dumps(obj, cls=ConfigEncoder, indent=4)

# Returns Json of config file
# if file doesant exist, create one from hardcoded default
def get_config(loc: Path=configPath):
    """Get config file from location.

    Args:
        loc (Path, optional): [description]. Defaults to configPath.

    Raises:
        IOError: Config is not readable. Check permissions, run as admin (unsafe), contact dev.
        HjsonDecodeError: Config's HJSON empty.

    Returns:
        [type]: [description]
    """    
    hjsonO = {}
    configlines = ""
    try:
        if not Path(loc).exists():
            config = BaseConfig()
            config.write_config_file()
        
        with open(loc, "r") as config_file:
            if not config_file.readable():
                logging.error("Config File Not Readable")
            
            hjsonO = load(config_file)
        if len(hjsonO) == 0:
            logging.debug("Config HJSon Object Empty")
            try:
                logging.info(f"Trying to erase empty config at {configPath}")
                os.remove(configPath.absolute())
            except PermissionError as e:
                logging.debug(f"""Failed to delete config.hjson due to a Permission error:
                              {e.__cause__}""")
                logging.debug("Delete config.hjson manually!")
            except Exception as e:
                logging.debug(e.__cause__)
                config = BaseConfig()
                config._location = loc
                return config
        else:     
            return BaseConfig(hjsonO)
    except HjsonDecodeError as error:
        logging.warning("Config file is likely malformed, remaking config.")
        backup_config(loc)
        config = BaseConfig()
        config._location = loc
        config.write_config_file()
        return BaseConfig()
            


def get_profiles(config: BaseConfig):
    return config.profiles

def add_profile(config: BaseConfig, profile: Profile):
    config.profiles.append(profile)
    config.write_config_file()
    
def backup_config(oldloc=configPath, retry=True):        
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
class ConfigEncoder(HjsonEncoder):  
    def default(self, obj):
        
        if isinstance(obj, BaseConfig):
            return self.default(obj.json())
        if isinstance(obj, version.Version | version.LegacyVersion):
            return obj.__str__()
        if type(obj) is Profile:
            return dict(self.ParseProfile(obj))
            
        if isinstance(obj, list) and len(obj) > 0:
            print("Parsing List:")
            # print(f"Encoding List of {type(obj[0])}")
            # if isinstance(obj[0], Request):
            #     print("\t\t\tEncoding Request List")
            #     for index, req in enumerate(obj):
            #         obj[index] = self.default(req)
            #     return self.default(obj)
            if isinstance(obj[0], Profile):
                print("\tEncoding Profile List")
                for index, profile in enumerate(obj):
                    obj[index] = self.default(profile)
                return list(obj)
            
        if isinstance(obj, tkinter.StringVar):
            return obj.get()
            
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            if isinstance(obj, dict):
                if ("profiles" or "requests") in obj.keys():
                    # If obj looks like {profiles: [{?, requests: [{}]}]} or basically list[dict[list[dict]]]
                    if isinstance(obj["profiles"], list) and isinstance(obj["profiles"][len(obj["profiles"]) - 1], dict) and isinstance(obj["profiles"][len(obj["profiles"]) - 1]["requests"], list) and isinstance(obj["profiles"][len(obj["profiles"]) - 1]["requests"][len(obj["profiles"][len(obj["profiles"]) - 1]["requests"]) - 1], dict):
                        return obj
                    else:
                        finalDict = {}
                        for key in obj:
                            finalDict.update({key:self.default(obj[key])})
                        return self.default(finalDict)
                        
                else: return obj
        
        if isinstance(obj, MappingProxyType):
            return self.default(dict(obj))
        
        return HjsonEncoder.encode(self, obj)

    def ParseList(self, obj):
        # print(f"Encoding List of {type(obj[0])}")
        if isinstance(obj[0], Request):
            print("\t\tEncoding Request List")
            for i in obj:
                return self.default(i)
        elif isinstance(obj[0], Profile):
            print("Encoding Profile List")
            for profile in obj:
                self.default(profile)
        else:
            return HjsonEncoder.default(self, obj)
    
    def ParseRequest(self, obj: Request):
        print("\t\t\t\t\tEncoding Request")
        if isinstance(obj, Request):
            return obj.json()
        elif isinstance(obj, dict):
            return obj
        
    def ParseProfile(self, obj: Profile):
        print("\t\tEncoding Profile:")
        profile =  obj.json()
        for index, request in enumerate(profile["requests"]):
            profile["requests"][index] = self.ParseRequest(request)
        return profile
