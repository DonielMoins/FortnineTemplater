from typing import Dict, Optional
from classes.requestObj import Request, comments as requestComments

class Profile():
    def __init__(self, ProfileName = "Default Name", Requests=[Request()], settings: Optional[dict] = {}, **kwargs):
        self.ProfileName = ProfileName
        self.Requests = Requests
        
        # at this point im just typing in english
        if len(settings) != 0: self.__dict__.update(settings) 
        if len(kwargs) != 0: self.__dict__.update(kwargs) 
            

def comments():
    return [
        # TODO add character limit
            "ProfileName: Button Name",
            "Requests: List of Request Objects that will be run using input data.",
            {"Request:" : requestComments()}
        ]