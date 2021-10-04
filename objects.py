"""
Python file containing all objects used in FortnineTemplater
*ahem* except BaseConfig (in config.py)
"""

from constants import ProgramVersion
from collections import OrderedDict
from typing import List, Optional
from packaging import version

import uuid as id
import re


class Request:
    def __init__(self, reqtype: str = "GET", uri: str = "https://example.com/test?", data_params: str = None, headers: dict = None, reuseSession: bool = True, **kwargs):
        """Creeate Request Object for use with functions from requests.py

        Args:
            reqtype (string): Set request type. Defaults to "get". 
                Supported Types: 
                        get
                        head
                        post
                        patch
                        put
                        delete
                        options
            uri (string): Set request uri.
            headers ([dict], optional): Set request headers. 
                Defaults to {
                    "User-Agent": "FortnineActions/Constants.ProgramVersion",
                    "Content-Type": "text",
                    'Accept': '*/*',
                }
            Info @ https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
            reuseSession ([bool], optional): If MakeRequest should reuse Session Object. Defaults to True.

        Raises:
            ValueError: Request type unknown.
            ValueError: Request Type unsupported.
        """

        self.__dict__.update(kwargs)
        self.reqtype: str = reqtype.casefold()
        self._uri = uri
        self.reuseSession = reuseSession
        self.headers = {
            "User-Agent": f"FortnineActions/{ProgramVersion.__str__()}",
            "Content-Type": "text",
            'Accept': '*/*',
        } if not headers else headers
        self.data_params = data_params
        # self.log_level = 4  # 0 Most verbose - 4 log on error - 5 Silent
        self.log_level = 0  # 0 Most verbose - 4 log on error - 5 Silent

        # Check if request type is supported with these 3 Cases:
        # If Request Type is supported, Ignore.
        # If not supported or if unknown request type, raise ValueError with appropriate message
        if self.reqtype in {"get", "head", "post", "patch", "put", "delete", "options"}:
            pass
        elif self.reqtype == ("connect", "request", "trace"):
            raise ValueError("Unsupported Request Type")
        else:
            raise ValueError(f"Unknown Request Type: '{self.reqtype}'")

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, value):
        match = re.match(r"((?:https|http)?:\/\/){1}((?:[-a-z0-9._~!$&\'()*+,;=]|%[0-9a-f]{2})+(?::(?:[-a-z0-9._~!$&\'()*+,;=]|%[0-9a-f]{2})+)?@)?(?:((?:(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.){3}(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5]))|((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z][a-z0-9-]*[a-z0-9]))(:\d+)?((?:\/(?:[-a-z0-9._~!$&\'()*+,;=:@]|%[0-9a-f]{2})+)*\/?)(\?(?:[-a-z0-9._~!$&\'()*+,;=:@\/?]|%[0-9a-f]{2})*)?",
                         value)
        assert match
        self._uri = match.string

    def json(self):
        d = {k: getattr(self, k, '') for k in self.__dir__() if k[:2] != "__" and k[:1] != "_" and type(
            getattr(self, k, '')).__name__ != "method"}
        return d


# Profile Contains Profile Name, List of Requests and an optional dictionary for profile settings.
# UUID MUST BE UNIQUE
# ? **kwargs overrides all settings
class Profile:
    def __init__(self, profileName: str = "Default Name", uuid: str = str(id.uuid4()), requests: List[Request] = [Request()], settings: dict = {}, version: Optional[version.Version] = None, migrateData: bool = False, **kwargs):
        self.profileName = profileName
        self.uuid = uuid
        self.settings = settings

        self.__dict__.update(kwargs)
        # "requests" in vars(self).keys()
        if requests and isinstance(requests, list):
            if all([isinstance(req, OrderedDict) for req in requests]):
                self.requests = [Request(**req) for req in requests]
            elif all([isinstance(req, Request) for req in requests]):
                self.requests = requests

        # Check if required variables exist.
        assert self.profileName
        assert self.uuid
        assert self.requests

        if version:
            if migrateData:
                self.MigrateProfile(version)

    def MigrateProfile(self, resultVersion):
        if not resultVersion:
            resultVersion = ProgramVersion
        # Check if specific version needs specific migration
        
        #? Add if statements for version numbers then run this func recusively till desired version migration has been achieved
        
        # match resultVersion:
        #     case version.Version("99.99.99"):  # Add broken config fixes
        #         # Specific Fixes
        #         pass
        #     case _:
        #         pass

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
