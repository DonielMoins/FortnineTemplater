"""
Python file containing all objects used in FortnineTemplater
*ahem* except BaseConfig (in config.py)
"""

from packaging import version
from collections import OrderedDict
from typing import List, Optional
import uuid as id

from utils.general import compareVersion
from constants import ProgramVersion


class Request:
    def __init__(self, dict={}):
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
        self.reqtype = str(dict.get("reqtype", "get")).lower()
        self.uri = dict.get(
            "uri", "https://example.com/api?requestParm1={0}&requestParm2={1}")

        """
        If you update the default headers Change Docstring.
        Find headers @ https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
        """
        self.headers = dict.get("headers", {
            "User-Agent": f"FortnineActions/{ProgramVersion.__str__()}",
            "Content-Type": "text",
            'Accept': '*/*',
        })
        self.reuseSession = dict.get("reuseSession", True)
        # self.__dict__.update(dict)

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
# UUID MUST BE UNIQUE
class Profile:
    def __init__(self, ProfileName: str = "Default Name", uuid: str = str(id.uuid4()), Requests: List[Request] = None, Settings: dict = None, version: Optional[version.Version | version.LegacyVersion] = None, migrateData: bool = False, fromDict: OrderedDict = None):
        if fromDict:
            self.profileName = fromDict.get("profileName", "Default Name")
            self.uuid = fromDict.get("uuid", str(id.uuid4()))
            self.requests = fromDict.get("requests", [Request()])
            self.settings = fromDict.get("settings", {})
            for index, req in enumerate(self.requests):
                if isinstance(req, OrderedDict):
                    self.requests[index] = Request(dict=req)
        else:
            self.profileName = ProfileName
            self.uuid = uuid
            if Requests:
                self.requests = Requests
            else:
                self.requests = [Request()]
            if Settings:
                self.settings = Settings
            else:
                self.settings = {}

        if version:
            if migrateData:
                self.MigrateProfile(version)

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

    def _serializeRequestList(self):
        requests = [request.json() for request in self.requests]
        return requests

    # def __getattribute__(self, item):
    #     if item == '__list__' and self.requests == item:
    #         if any(isinstance(x, Request) for x in list):
    #             self._serializeRequestList()
    #         return object.__getattribute__(self, item)

    #     return object.__getattribute__(self, item)

    def json(self):
        v = vars(self)
        v["requests"] = self._serializeRequestList()
        return v
