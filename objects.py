from typing import Optional

from requests import options


class Request():

    def __init__(self, **kwargs):
        self.reqtype = kwargs.get("reqtype", "get")
        self.uri = kwargs.get(
            "uri", "https://example.com/api?requestParm1={0}&requestParm2={1}")
        self.headers = kwargs.get("headers", {
            "user-agent": "FortnineActions/0.0.1",
            "content-type": "text"
        })
        self.ReuseSession = kwargs.get("ReuseSession", True)
        self.__dict__.update(kwargs)

        self.reqtype.lower()
        match self.reqtype:
            case "get":
                pass
            case "head":
                pass
            case "post":
                pass
            case "patch":
                pass
            case "put":
                pass
            case "delete":
                pass
            case "options":
                pass
            case _:
                raise Exception("Malformed Request Type JSON")


class Profile():
    def __init__(self, ProfileName="Default Name", Requests=[Request()], settings: Optional[dict] = {}):
        self.ProfileName = ProfileName
        self.Requests = Requests

        # at this point im just typing in english
        if len(settings) != 0:
            self.__dict__.update(settings)
