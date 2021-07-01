# Config I/O Handler.
from types import MappingProxyType
import hjson, logging, os
from hjson import HjsonEncoder, load, HjsonDecodeError
from pathlib import Path 
from objects import Profile, Request

# TODO: Make settings file window.
home_dir = Path(__file__).parent.parent
configPath = home_dir.joinpath("config.hjson")

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
                raise HjsonDecodeError("Config HJSon Object Empty", config_file.readline(), 0)
            if "IGNORED" in hjsonO.keys():
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
def write_config_file(settings= {}, loc=configPath):
    """Function to write config file

    Args:
        settings (dict, optional): Dictionary of all settings to write to file. Defaults to build_config() if None is provided.
        loc ([type], optional): Path of config.hjson file. Defaults to default_loc.

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

def get_profiles(jsonConfig):
    """Go through config, for each profile in config, create profile objects and then return them

    Args:
        jsonConfig (dict): The parsed Config.hjson as a dictionary.

    Returns:
        list[Profile]: List of Profile objects
    """
    profiles = []
    for profileDict in jsonConfig["profiles"]:
        profile = Profile(kwargs=profileDict) 
        profiles.append(profile)
    return profiles

        
def build_config():
    default_config = {
                    "profiles": [
                        Profile(),
                        Profile()
                        ]
                    }
    return default_config

class ConfigEncoder(HjsonEncoder):  
    def default(self, obj):
        
        if type(obj) is Profile:
            return self.ParseProfile(obj)
            
        if type(obj) is Request:
            return self.ParseRequest(obj)
            
        if isinstance(obj, list) and len(obj) > 0:
            print("Parsing List:")
            # print(f"Encoding List of {type(obj[0])}")
            if isinstance(obj[0], Request):
                print("\t\tEncoding Request List")
                for i in obj:
                    return self.default(i)
            if isinstance(obj[0], Profile):
                print("Encoding Profile List")
                for profile in obj:
                    self.default(profile)
            
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            # if profiles key is a dict, convert it to a list
            if type(obj) is dict and "profiles" in obj.keys() and isinstance(obj["profiles"], dict):
                obj["profiles"] = obj["profiles"].values()
                print("Converted dict profiles to list.")
                return self.default(obj)
            return HjsonEncoder.default(self, obj)
        
        if isinstance(obj, MappingProxyType):
            return self.default(dict(obj))
        
        return HjsonEncoder.default(self, obj)

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
            HjsonEncoder.default(self, obj)
    
    def ParseRequest(self, obj: Request):
        print("\t\t\tEncoding Request")
        return obj.json()
        
    def ParseProfile(self, obj: Profile):
        print("\tEncoding Profile:")
        return obj.json()
            