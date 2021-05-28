
from objects.requestObj import Request
from objects.requestObj import comments as requestComments

class Profile():
    def __init__(self, **kwargs):
        if len(kwargs) is not 0:
            self.__dict__ = kwargs
        else:
            self.ProfileName = "Default Name"
            self.Requests = [Request()]
            

def comments():
    return [
        # TODO add character limit
            "ProfileName: Button Name",
            "Requests: List of Request Objects that will be run using input data.",
            {"Request:" : requestComments()}
        ]