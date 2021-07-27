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
logger = logging.getLogger(__name__)

def makeRequest(requestTemplate: ReqObj, keys: Optional[list[str]], data: Optional[list[str]], session: requests.Session):
    reqtype = requestTemplate.reqtype
    response = None

    """
    ? Add:
    ?     case reqtype:
    ? if you want to make special adjustments to how we handle requests.
    
    If Unknown reqtype, warn in logs, then return response with status code 405.
    """
    match requestTemplate.reqtype:
        case  "post" | "put":
            URL, payload = makeData(requestTemplate.uri, data)
            request = requests.Request(str(reqtype).upper(), URL, data=payload)
            request.data = payload
            
        case "get" | "head" | "patch" | "delete" | "options":
            URL = parseURL(requestTemplate.uri, data)
            request = requests.Request(str(reqtype).upper(), URL)
            prepedreq = session.prepare_request(request)
            
        case _:
            logger.warn(
                f"Unknown request method {str(requestTemplate.reqtype)} in {repr(requestTemplate)}")
            logger.debug("How did this request get past checks")
            # Create fake response to return with status_code 405
            response = requests.Response()
            response.status_code = 405      # Status Code 405: Method Not Allowed
        
    prepedreq = session.prepare_request(request)
    response: requests.Response = session.send(prepedreq)
    return response


def MakeRequests(requestList: list, fieldDataList: list = None, uuid=None, stateSender: Connection = None, session=requests.Session()):
    Responses = []
    sendProg = False
    if stateSender and uuid:
        sendProg = True
        stateSender.send(f"{uuid}: 0.0")
    for reqIndex, request in enumerate(requestList):
        request: ReqObj
        if fieldDataList:
            for inputDataIndex, data in enumerate(fieldDataList[reqIndex]):
                Responses.append(makeRequest(request, data, session))
                if sendProg:
                    stateSender.send(
                        f"{uuid}: {((inputDataIndex + 1)/len(fieldDataList[reqIndex]))+((reqIndex + 1)/len(requestList))*100 - 1}")
        else:
            Responses.append(makeRequest(request, None, session))
            if sendProg:
                stateSender.send(
                    f"{uuid} : {(reqIndex + 1)/len(requestList)*100}")
    return Responses


def parseURL(uri: str, data: Optional[list[str]]):
    finalURI: str = uri
    if data is not None:
        matches = re.findall("{[0-9]+}", uri)
        if len(matches) <= len(data):
            for index, match in enumerate(matches):
                finalURI = finalURI.replace(match, data[index])
        else:
            logger.warn("Not enough input present.")
    return finalURI

def makeData(uri: str, data: Optional[list[str]]):
    # Thank god for list comprehensions.
    # Matches the queries into groups that start with "?" or "&", then before adding matches clean up the "?" and "&"
    keys = [match.replace("&", "").replace("?", "") for match in re.split(uri, r"[\?&](\w+)=(\w+)")]
    cleanURL = uri[ : uri.rfind("?")]
    payload = {keyVal: data[index] for index, keyVal in enumerate(keys)}
    return cleanURL, payload

# def getMatches(Request: ReqObj.Request):
#     return re.findall("/{([0-9])+}/g", Request.uri)
