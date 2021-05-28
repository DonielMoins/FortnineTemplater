from requests.api import request, get, head, post, patch, put, delete, options

class Request():
    
    def __init__(self, **kwargs):
        if len(kwargs) != 0:
            self.__dict__ = kwargs
            self.reqtype.lower()
            if self.reqtype != "request" or "get" or "head" or "post" or "patch" or "put" or "delete" or "options":
                raise Exception("Malformed Request Type JSON") 
        else:
            self.uri = "https://example.com/api?requestParm1={0}&requestParm2={1}"
            self.reqtype = "get"
            self.headers = {
                "user-agent": "FortnineActions/0.0.1",
                "content-type":"text"
                }
            self.ReuseSession = True




def comments():
    return {
            "request-uri (string)" : "anything between {} containing a number will be understood as a parameter,",
            "~~~~~~~~~~~~~~~~~~~~" : "if it does not contain a number, you will be shamed!",
            "~~~~~~~~~~~~~~~~~~~~" : "https://domain.tls/exampleParm1-999={0-999}",
            "type (string)" : "one of the following options",
            "~~~~~~~~~~~~~" : "request, get, head, post, patch, put, delete, options",
            
            "headers (dict of str)" :
                {
                    "ex.":{
                        "user-agent": "FortnineActions/0.0.1",
                        "content-type":"text"
                        },
                    "DOCS": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers"
                }
                 
                
            }
            
            
    