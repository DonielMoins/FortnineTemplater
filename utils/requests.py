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


def makeRequest(requestTemplate: ReqObj, linkData: Optional[list[str]], postData: Optional[list[str]], session: requests.Session):
    reqtype = requestTemplate.reqtype
    response = None

    if not (isinstance(requestTemplate, ReqObj) and isinstance(linkData, list or None) and isinstance(postData, list or None), isinstance(session, requests.Session)):
        logger.error(
            f"""Incorrect parameters passed to makeRequest Function.
            ReqTemp: {type(requestTemplate)}, {requestTemplate}
            linkData: {type(linkData)}, {linkData}
            postData: {type(postData)}, {postData}
            session: {type(session)}, {session}
            """)

    # If Unknown reqtype, warn in logs, then return response with status code 405.

    match reqtype:
        case  "post" | "put":
            URL = parseURL(requestTemplate.uri, linkData)
            payload = makeData(requestTemplate.data_params, postData)
            request = requests.Request(str(reqtype).upper(), URL, data=payload)

        case "get" | "head" | "patch" | "delete" | "options":
            URL = parseURL(requestTemplate.uri, linkData)
            request = requests.Request(str(reqtype).upper(), URL)
            prepedreq = session.prepare_request(request)

        case _:
            logger.warn(
                f"Unknown request method {str(reqtype)} in {repr(requestTemplate)}")
            logger.debug("How did this request get past checks")
            # Create fake response to return with status_code 405
            response = requests.Response()
            response.status_code = 405      # Status Code 405: Method Not Allowed
            return response

    response: requests.Response = session.send(prepedreq)
    return response


def MakeRequests(requestList: list, linkDataList: list = None, postDataList: list = None, uuid=None, stateSender: Connection = None):

    Responses = []
    session = requests.Session()
    _oldHeaders = session.headers

    if stateSender and uuid:
        sendProg = True
        stateSender.send(f"{uuid}: 0.0")
    else:
        sendProg = False

    for reqIndex, request in enumerate(requestList):
        request: ReqObj
        session.headers = request.headers if request.reuseSession else _oldHeaders
        if linkDataList:
            for inputDataIndex, linkData in enumerate(linkDataList[reqIndex]):
                match request.reqtype:
                    case "post" | "put":
                        for postDataIndex, postData in enumerate(postDataList[reqIndex]):
                            # just a sanity check
                            if isinstance(postData, list):
                                Responses.append(makeRequest(
                                    request, linkData, postData, session))
                                if sendProg:
                                    stateSender.send(
                                        f"{uuid}: {((inputDataIndex + 1)/len(linkDataList[reqIndex]))+((reqIndex + 1)/len(requestList))*100 - 1}")
                    case _:
                        Responses.append(makeRequest(
                            request, linkData, None, session))
                        if sendProg:
                            stateSender.send(
                                f"{uuid}: {((inputDataIndex + 1)/len(linkDataList[reqIndex]))+((reqIndex + 1)/len(requestList))*100 - 1}")

        else:
            Responses.append(makeRequest(
                request, None, None if not request.data_params or "NULL" else request.data_params, session))
            if sendProg:
                stateSender.send(
                    f"{uuid} : {(reqIndex + 1)/len(requestList)*100}")
    sendProg: stateSender.send(
        f"{uuid}: 100")
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


def makeData(template_json: str, data: Optional[list[str]]):
    # in case data is empty
    assert template_json
# TODO: Add string / number parsing
    if data and data != "NULL":
        pJson = template_json
        matches = re.findall("{[0-9]+}", template_json)
        if len(matches) <= len(data):
            for index, match in enumerate(matches):
                payload = pJson.replace(match, data[index])
    else:
        payload = template_json
    return payload

# def getMatches(Request: ReqObj.Request):
#     return re.findall("/{([0-9])+}/g", Request.uri)
