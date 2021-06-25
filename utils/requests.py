from multiprocessing.connection import Connection
from typing import Optional
import re 
import requests
from objects import Request as ReqObj
import logging

# NOTE USE IN THREAD FROM THREADPOOL OR ELSE BLOCKING
# make single request checking what type from template
def makeRequest(requestTemplate: ReqObj, data: list[str], session: requests.Session):
    reqtype = requestTemplate.reqtype
    
    
    URL = parseLink(requestTemplate.uri, data)
    request = requests.Request(str(reqtype).upper(), URL)
    
    
    # TODO see what special options we need for each request method.
    match requestTemplate.reqtype:
        case "request":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case "get":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case "head":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case "post":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case "patch":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case "put":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case "delete":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case "options":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case _:
            logging.warn(f"Unknown request method {str(requestTemplate.reqtype)} in {repr(requestTemplate)}")
            logging.debug("How did this request get past checks")
    
def MakeRequests(requestList: list, dataList: list[list[str]], Identifier=None, progressConn: Connection=None, session=requests.Session()):
    if progressConn and Identifier:
        sendProg = True
    else:
        sendProg = False
    for request in requestList:
        request: ReqObj.Request = request
        if dataList is not None:
            for index, data in enumerate(dataList):
                makeRequest(request, data, session)
                progressConn.send({Identifier: float(index + 1)/len(dataList)})
        else:
            
            makeRequest(request, None, session)
            if progressConn and Identifier:
                progressConn.send({Identifier: 100.0})

def parseLink(uri: str, data: Optional[list[str]]):
    finalURI = uri
    if data is not None:
        matches = re.findall("/{([0-9])+}/g", uri)
        if len(matches) <= len(data):
            for index, match in enumerate(matches):
                finalURI.replace(match, data[index])
        else:
            logging.warn("Not enough input present.")
    return finalURI
        
# def getMatches(Request: ReqObj.Request):
#     return re.findall("/{([0-9])+}/g", Request.uri)