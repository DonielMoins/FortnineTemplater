import requests
import objects.requestObj as requestObj

# NOTE USE IN THREAD FROM THREADPOOL OR ELSE BLOCKING
# make single request checking what type from template
def makeRequest(requestTemplate: requestObj, data=None, session=None):
    if requestTemplate.ReuseSession and session is None:
        session = requests.Session()
    
    reqtype = requestTemplate.reqtype
    # TODO: Using python 3.10 we can use PEP 634 (match and case) but too bad its a pain in the ass to upgrade.
    if reqtype is "request":
        pass
    elif reqtype is "get":
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
    
    
        