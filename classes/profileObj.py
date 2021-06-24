from typing import Dict, Optional
from classes.requestObj import Request # comments as requestComments

class Profile():
    def __init__(self, ProfileName = "Default Name", Requests=[Request()], settings: Optional[dict] = {}):
        self.ProfileName = ProfileName
        self.Requests = Requests
        self.saveSession = False
        
        # at this point im just typing in english
        if len(settings) != 0: self.__dict__.update(settings) 
            

# def comments():
#     return [
#             "ProfileName: Button Name",
#             "Requests: List of Request Objects that will be run using input data.",
#             {"Request:" : requestComments()}
#         ]