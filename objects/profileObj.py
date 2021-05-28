
from requestObj import Request

class Profile():
    ProfileName = "Default Name"
    Request = Request()
    
    def __init__(self, **kwargs):
        if len(kwargs) is not 0:
            self.__dict__ = kwargs

#{
#                            "request-uri"   : "",
#                            "type"          : "GET",
#                            "headers"       : {
#                                'user-agent': 'FortnineActions/0.0.1'
#                            },
#                          }

def comments():
    return [
            """request-uri: anything between {} that has var then a number will be understood as a parameter
                                https://domain.tls/exampleParm1-999={var0-999}""",
            """type: one of these options: 
                    request, get, head, post, patch, put, delete, options""",
            """headers: """
            ]