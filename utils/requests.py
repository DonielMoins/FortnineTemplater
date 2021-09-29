from multiprocessing.connection import Connection
from utils.general import banner, makeLogger
from objects import Request as ReqObj
from threading import current_thread
from datetime import datetime
from typing import Optional
from constants import tab
import requests
import logging
import re


"""
 * NOTE USE IN THREAD FROM THREADPOOL OR ELSE BLOCKING
 * make single request checking what type from template
"""
logger = logging.getLogger(current_thread().name)
console_handler = logging.StreamHandler()


def makeRequest(requestTemplate: ReqObj, linkData: Optional[list[str]], postData: Optional[list[str]], session: requests.Session, logger: logging.Logger):
    reqtype = requestTemplate.reqtype
    response = None
    execTime = datetime.now()

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
            prepedreq = session.prepare_request(request)

        case "get" | "head" | "patch" | "delete" | "options":
            URL = parseURL(requestTemplate.uri, linkData)
            request = requests.Request(str(reqtype).upper(), URL)
            prepedreq = session.prepare_request(request)

        case _:
            logger.warn(
                f"Unknown request method {str(reqtype)} in {repr(requestTemplate)}")
            logger.debug("How did this request get past checks...")
            # Create fake response to return with status_code 405
            response = requests.Response()
            response.status_code = 405      # Status Code 405: Method Not Allowed
            return response

    response: requests.Response = session.send(prepedreq)
    return (execTime, response)


def MakeRequests(requestList: list, linkDataList: list = None, postDataList: list = None, uuid: str = None, stateSender: Connection = None, log: bool = True):
    makeLogger()
    session = requests.Session()
    _oldHeaders = session.headers
    Responses = []

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
                        for postData in postDataList[reqIndex]:
                            # just a sanity check
                            if isinstance(postData, list):
                                Responses.append(makeRequest(
                                    request, linkData, postData, session, logger))
                                if sendProg:
                                    stateSender.send(
                                        f"{uuid}: {((inputDataIndex + 1)/len(linkDataList[reqIndex]))+((reqIndex + 1)/len(requestList))*100 - 1}")
                    case _:
                        Responses.append(makeRequest(
                            request, linkData, None, session, logger))
                        if sendProg:
                            stateSender.send(
                                f"{uuid}: {((inputDataIndex + 1)/len(linkDataList[reqIndex]))+((reqIndex + 1)/len(requestList))*100 - 1}")

        else:
            Responses.append(makeRequest(
                request, None, None if not request.data_params or "NULL" else request.data_params, session, logger))
            if sendProg:
                stateSender.send(
                    f"{uuid} : {(reqIndex + 1)/len(requestList)*100}")
    sendProg: stateSender.send(f"{uuid}: 100")
    if log:
        logger.info(banner(f"Responses of {uuid}"))
        for n, data in enumerate(Responses):
            time, res = data
            res: requests.Response
            time: datetime
            # For intellisense

            logger.info(
                banner(f"Response {n + 1}/{len(Responses)} @ {time.strftime('%Y-%m-%d %H:%M:%S')}"))
            logger.info(f"URL: {res.request.url}")
            logger.info(f"{2 * tab}Status Code: {res.status_code}")
            if res.status_code != 200:
                logger.info(f"{2 * tab}Content:")
                content = str(res.content).removeprefix(
                    "b'").removesuffix("'").removesuffix("\\n").split("\\n")
                for line in content:
                    logger.info(3 * tab + line)
            logger.info(banner(""))
    return Responses


def parseURL(uri: str, data: Optional[list[str]]):
    makeLogger()
    finalURI: str = uri
    if data is not None:
        matches = re.findall("{[0-9]+}", uri)
        if len(matches) <= len(data):
            for index, match in enumerate(matches):
                finalURI = finalURI.replace(match, data[index])
        else:
            logger.warning("Not enough input present in URL data.")
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
