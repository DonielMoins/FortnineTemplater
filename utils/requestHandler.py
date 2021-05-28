import requests
import objects.requestObj as requestObj

# NOTE USE IN THREAD FROM THREADPOOL OR ELSE BLOCKING
# make single request checking what type from template
def makeRequest(requestTemplate: requestObj, data=None, session=requests.Session()):
    reqtype = requestTemplate.reqtype
    
    URL = requestTemplate.uri
    request = requests.Request(str(reqtype).upper(), URL)
    
    # TODO: Using python 3.10 we can use PEP 634 (match and case) but too bad its a pain in the ass to upgrade.
    if reqtype == "get":
        prepedreq = session.prepare_request()
        response: requests.Response = session.send(prepedreq)
    elif reqtype == "head":
        prepedreq = session.prepare_request()
        response: requests.Response = session.send(prepedreq)
    elif reqtype == "post":
        prepedreq = session.prepare_request()
        response: requests.Response = session.send(prepedreq)
    elif reqtype == "patch":
        prepedreq = session.prepare_request()
        response: requests.Response = session.send(prepedreq)
    elif reqtype == "put":
        prepedreq = session.prepare_request()
        response: requests.Response = session.send(prepedreq)
    elif reqtype == "delete":
        prepedreq = session.prepare_request()
        response: requests.Response = session.send(prepedreq)
    else:
        # OPTIONS REQUEST
        prepedreq = session.prepare_request()
        response: requests.Response = session.send(prepedreq)
    
def MakeRequests(requestList: list, data=None, session=requests.Session()):
    for request in requestList:
        request: requestObj.Request = request
        makeRequest(request, data=data session=session)
        