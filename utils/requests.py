from multiprocessing.connection import Connection
from typing import Optional
import re
import requests
from objects import Request as ReqObj
import logging

"""
 * NOTE USE IN THREAD FROM THREADPOOL OR ELSE BLOCKING
 * make single request checking what type from template
"""

def makeRequest(requestTemplate: ReqObj, data: list[str], session: requests.Session):
    reqtype = requestTemplate.reqtype

    URL = parseLink(requestTemplate.uri, data)
    request = requests.Request(str(reqtype).upper(), URL)
    response = None

    """
    ? Add:
    ?     case reqtype:
    ? if you want to make special adjustments to how we handle requests.
    
    If Unknown reqtype, warn in logs, then return response with status code 405.
    """
    match requestTemplate.reqtype:
        case "get" | "head" | "post" | "patch" | "put" | "delete" | "options":
            prepedreq = session.prepare_request(request)
            response: requests.Response = session.send(prepedreq)
        case _:
            logging.warn(
                f"Unknown request method {str(requestTemplate.reqtype)} in {repr(requestTemplate)}")
            logging.debug("How did this request get past checks")
            response = requests.Response()  # Create fake response to return with status_code 405
            response.status_code = 405      # Status Code 405: Method Not Allowed
    return response


def MakeRequests(requestList: list, dataList: list[list[str]] = None, Identifier=None, progressConn: Connection = None, session=requests.Session()):
    Responses = []
    for request in requestList:
        request: ReqObj.Request = request
        if not dataList:
            for index, data in enumerate(dataList):
                Responses.append(makeRequest(request, data, session))
                progressConn.send(f"{Identifier}: {float(index + 1)/len(dataList)}")
        else:
            Responses.append(makeRequest(request, None, session))
            if progressConn and Identifier:
                progressConn.send(f"{Identifier} : 100.0")
    return Responses


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
