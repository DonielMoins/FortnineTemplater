"""
Python file containing objects used in FortnineTemplater

Syntax: 
    [Object ([Option : Option Type])] : [Description]
    Profile (ProfileName : str, Requests : List[Request], Settings : Optional[Dict]) : 
                Profile Object containing a List[Request], 
                Profile Name used in config,
                Optional Settings to be used later.
"""

import hjson
from typing import Optional

from utils.general import compareVersion, ProgramVersion

from packaging import version


class Request():
    def __init__(self, **kwargs):
        """Creeate Request Object for use with functions from requests.py
        
        Args:
            reqtype ([string], optional): Set request type. Defaults to "GET". 
                Supported Types: 
                        Get
                        Head
                        Post
                        Patch
                        Put
                        Delete
                        Options
            uri ([string], optional): Set request uri. Defaults to "https://example.com/api?requestParm1={0}&requestParm2={1}".
            headers ([dict], optional): Set request headers. 
                Defaults to {
                    "User-Agent": "FortnineActions/0.0.1",
                    "Content-Type": "text",
                    'Accept': '*/*',
                }
            reuseSession ([bool], optional): If MakeRequest should reuse Session Object. Defaults to True.
            
        Raises:
            ValueError: Request type unknown.
            ValueError: Request Type unsupported.
        """        
        self.reqtype = kwargs.get("reqtype", "get").lower()
        self.uri = kwargs.get(
            "uri", "https://example.com/api?requestParm1={0}&requestParm2={1}")
        
        """
        If you update the default headers Change Docstring.
        Find headers @ https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
        """
        self.headers = kwargs.get("headers", {
            "User-Agent": f"FortnineActions/{ProgramVersion.__str__}",
            "Content-Type": "text",
            'Accept': '*/*',
        })
        self.reuseSession = kwargs.get("reuseSession", True)
        self.__dict__.update(kwargs)
        
        # Check if request type is supported with these 3 Cases:
        match self.reqtype:
            # If Request Type is supported, Ignore.
            case "get" | "head" | "post" | "patch" | "put" | "delete" | "options":
                pass
            # If not supported or if unknown request type, raise ValueError with appropriate message 
            case "connect" | "request" | "trace":
                raise ValueError("Unsupported Request Type")
            case _:
                raise ValueError(f"""
                                 Unknown Request Type: '{self.reqtype}'
                                    Supported Values (Case-Insensitive):
                                        Get (Tested)
                                        Head (Untested)
                                        Post (Tested)
                                        Patch (Untested)
                                        Put (Untested)
                                        Delete (Untested)
                                        Options (Untested)"""
                                        )
    def json(self):
        return vars(self)



# Profile Contains Profile Name, List of Requests and an optional dictionary for profile settings.
class Profile():
    def __init__(self, ProfileName="Default Name", Requests=[Request()], Settings: Optional[dict] = {}, migrateData = False, version: Optional[version.Version] = ProgramVersion, **kwargs):
        self.profileName = ProfileName
        self.requests = Requests
        self.settings = Settings
        if migrateData:
            self.MigrateProfile(version)
        if not kwargs:
            self.__dict__.update(kwargs)
        

    def MigrateProfile(self, resultVersion):
        if not resultVersion:
            resultVersion = ProgramVersion
        # Check if specific version needs specific migration
        match resultVersion:
            case version.Version("Broken.Profile.Version"):
                # Specific Fixes
                pass
            case _:
                pass
        
        
    def json(self):
        return vars(self)
        

