from requests.api import request, get, head, post, patch, put, delete, options

class Request():
    
    uri = "https://example.com/api?requestParm1={var0}&requestParm2={var1}"
    reqtype = "get"
    headers = {
                'user-agent': 'FortnineActions/0.0.1'
                }
    ReuseSession = True
    
    def __init__(self, **kwargs):
        if len(kwargs) is not 0:
            self.__dict__ = kwargs
            self.reqtype.lower()
            if self.reqtype is not "request" or "get" or "head" or "post" or "patch" or "put" or "delete" or "options":
                raise Exception("Malformed Request Type JSON") 
            
            
    