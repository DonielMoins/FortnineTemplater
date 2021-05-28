import requests
import objects.requestObj as requestObj # pylint: disable=import-error

# make single request checking what type from template
def makeRequest(requestTemplate: requestObj, data=None, session=None):
    if requestTemplate.ReuseSession and session is None:
        session = requests.Session()
    
    reqtype = requestTemplate.reqtype
    # TODO: Using python 3.10 we can use PEP 634 (match and case)
    #  or "get" or "head" or "post" or "patch" or "put" or "delete" or "options"
    if reqtype is "request":
        pass
    elif reqtype is "head":
        pass
    elif reqtype is "post":
        pass
    elif reqtype is "patch":
        pass
    elif reqtype is "put":
        pass
    elif reqtype is "delete":
        pass
    else:
        pass
    
    
        