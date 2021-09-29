# Config I/O Handler file with multiple functions to manipulate the
# storing/deleting/editing of profiles in the config file.
from hjson import HjsonEncoder, HjsonDecodeError, load
from configparser import ConfigParser
from constants import ProgramVersion
from objects import Profile, Request
from collections import OrderedDict
from types import MappingProxyType
from pathlib import Path
from packaging import version

import tkinter
import logging
import hjson
import os

logger = logging.getLogger("Config")

# TODO: Make settings file window.
home_dir = Path(__file__).parent.parent
configPath = home_dir.joinpath("config.hjson")


class BaseConfig(object):
    def __init__(self, configVersion=None, profiles=None, settings={}, path: Path = None, **kwargs):
        # Will first check if argument in kwargs, if not, check if passed as argument, if not use defaults.
        # Defaults to configVersion if settings is None
        self.configVersion = kwargs.get(
            "configVersion", str(ProgramVersion) if not configVersion else configVersion)
        # Defaults to [Profile(fromDict={}), Profile(fromDict={})] if profiles is None
        self.profiles = kwargs.get(
            "profiles", [Profile(), Profile()] if not profiles else profiles)
        # Defaults to {} if settings is None
        self.settings = kwargs.get(
            "settings", {} if not settings else settings)
        # Defaults to configPath if path is None
        self._location: Path = kwargs.get(
            "path", configPath if not path else path)
        for index, profile in enumerate(self.profiles):
            if isinstance(profile, OrderedDict):
                profileObj = Profile(**profile)
                self.profiles[index] = profileObj

    def write_config_file(self, loc: Path = None):
        """Function to write config file

        Args:
            settings (dict, optional): Dictionary of all settings to write to file. Defaults to build_config() if None is provided.
            loc (Path, optional): Path of config.hjson file. Defaults to default_loc.

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


def get_config(loc: Path = configPath):
    """Make BaseConfig class from given config file. 
    Defaults to config.configPath.

    Args:
        loc (Path, optional): Path of config file. Defaults to configPath.

    Raises:
        IOError: Config is not readable. Check permissions, run as admin (unsafe), contact dev.
        HjsonDecodeError: Config's HJSON empty.

    Returns:
        BaseConfig: Serialized config data.
    """
    hjsonO = {}
    try:
        if not Path(loc).exists():
            config = BaseConfig()
            config.write_config_file()

        with open(loc, "r") as config_file:
            if not config_file.readable():
                logger.error("Config File Not Readable")

            hjsonO = load(config_file)
        if len(hjsonO) == 0:
            logger.debug("Config HJSon Object Empty")
            try:
                logger.info(f"Trying to erase empty config at {configPath}")
                os.remove(configPath.absolute())
            except PermissionError as e:
                logger.debug(f"""Failed to delete config.hjson due to a Permission error:
                              {e.__cause__}""")
                logger.debug("Delete config.hjson manually!")
            except Exception as e:
                logger.debug(e.__cause__)
                config = BaseConfig()
                config._location = loc
                return config
        else:

            return BaseConfig(**hjsonO)
    except HjsonDecodeError as error:
        logger.warning("Config file is likely malformed, remaking config.")
        backup_config(loc)
        config = BaseConfig()
        config._location = loc
        config.write_config_file()
        return config


def get_profiles(config: BaseConfig):
    return config.profiles


def add_profile(config: BaseConfig, profile: Profile):
    config.profiles.append(profile)
    config.write_config_file()


def del_profile(config: BaseConfig, profile: Profile):

    del_profile_uuid(config=config, uuid=profile.uuid)
    config.write_config_file()


def del_profile_uuid(config: BaseConfig, uuid: str):
    """Delete a profile by it's uuid from a given config.

    First goes through all profiles checking for a matching uuid, if one is found
        add profile's index in list to the to_remove.
            (Cannot remove it directly because you cannot change list size while iterating over it)
    Then for each item in to_remove, get the index value stored and remove it from config.profiles using .pop
        NOTE: Can use del instead of .pop, but .pop is prettier

    Args:
        config (BaseConfig): [description]
        uuid (str): uuid of profile to remove.
    """
    to_remove = []
    for index, prof in enumerate(config.profiles):
        if prof.uuid == uuid:
            to_remove.append(index)
    for i in to_remove:
        logger.warning(
            f"Removing Profile {config.profiles[i].profileName}({config.profiles[i].uuid}).")
        logger.warning(
            f"Printing backup of profile in-case of user 'error':\n {config.profiles[i].json()}")
        config.profiles.pop(i)


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
            # TODO Make this show a popup error screen.
            # raise FileExistsError("Config.yml already exists and retry mode is disabled")
            logger.error(
                "Config.yml already exists and retry mode is disabled")
    else:
        backuploc = Path(oldloc.__str__() + ".bak")

    with open(oldloc, "r") as old_file:
        old_data = old_file.readlines()

    with open(backuploc, "w") as backup_file:
        if backup_file.writable():
            backup_file.writelines(old_data)
        else:
            # TODO Make this show a popup error screen.
            logger.debug("Could not safely write backup config file!")
            logger.error(
                "Could not safely write backup config file! \n File not writable, check Folder permissions!")


class ConfigEncoder(HjsonEncoder):
    def default(self, obj):
        """
        Function called when class is passed as cls variable. 
        this function has to be overridden.

        Even I hate this Encoder. 
        """

        if isinstance(obj, BaseConfig):
            return self.default(obj.json())

        if isinstance(obj, version.Version | version.LegacyVersion):
            return str(obj)

        if isinstance(obj, Profile):
            return dict(self.ParseProfile(obj))

        if isinstance(obj, list) and len(obj) > 0 and any(isinstance(x, Profile) for x in obj):
            # print("\tEncoding Profile List")
            for index, profile in enumerate(obj):
                obj[index] = self.default(profile)
            return list(obj)

        if isinstance(obj, tkinter.StringVar):
            return obj.get()

        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            if isinstance(obj, dict):
                if ("profiles" or "requests") in obj.keys():
                    # If obj looks like {profiles: [{?, requests: [{}]}]} or basically list[dict[list[dict]]]
                    dictionary: dict = obj  # TODO Remove unnecessary line, only used for typing hints
                    if isinstance(obj["profiles"], list) and all(isinstance(x, Profile) for x in obj["profiles"]) and isinstance(obj["profiles"][len(obj["profiles"]) - 1]["requests"], list) and isinstance(obj["profiles"][len(obj["profiles"]) - 1]["requests"][len(obj["profiles"][len(obj["profiles"]) - 1]["requests"]) - 1], dict):
                        return obj
                    else:
                        finalDict = {}
                        for key in obj:
                            finalDict.update({key: self.default(obj[key])})
                        return self.default(finalDict)

                else:
                    return obj

        if isinstance(obj, MappingProxyType):
            return self.default(dict(obj))

        return HjsonEncoder.encode(self, obj)

    def ParseList(self, obj: list):
        # print(f"Encoding List of {type(obj[0])}")
        if isinstance(obj[0], Request):
            # print("\t\tEncoding Request List")
            for i in obj:
                return self.default(i)
        elif isinstance(obj[0], Profile):
            # print("Encoding Profile List")
            for profile in obj:
                self.default(profile)
        else:
            return HjsonEncoder.default(self, obj)

    def ParseRequest(self, obj: Request):
        # print("\t\t\t\t\tEncoding Request")
        if isinstance(obj, Request):
            return obj.json()
        elif isinstance(obj, dict):
            return obj

    def ParseProfile(self, obj: Profile):
        # print("\t\tEncoding Profile:")
        profile = obj.json()
        for index, request in enumerate(profile["requests"]):
            profile["requests"][index] = self.ParseRequest(request)
        return profile


class ConfigParserWrapper():
    pass


class HJSONConfigParser(ConfigParser):
    def __init_subclass__(cls):
        return super().__init_subclass__()
