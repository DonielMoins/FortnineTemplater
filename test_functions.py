from typing import List
import unittest
from bs4 import BeautifulSoup
from requests import Response
import requests
from utils.requests import MakeRequests, makeRequest
from utils.general import parseCSV, randomString, randomSymbols
from objects import Profile, Request
from unittest.mock import patch


class CSV_Tests(unittest.TestCase):

    def test_LargeOneLine_Default(self):
        maxParamSize = 10
        size = (100, 2)
        bigString = ""
        for indexX, i in enumerate(range(size[0])):
            for index, x in enumerate(range(size[1])):
                bigString += randomString(maxParamSize)
                if (index != size[1] - 1):
                    bigString += ","
            if (indexX != size[0] - 1):
                bigString += "\n"
        csv = parseCSV(bigString)

        # Check size
        self.assertTrue(len(csv) == size[0])
        self.assertTrue(len(csv[0]) == size[1])
        # Check csvlist structure
        self.assertIsInstance(csv, list)
        for line in csv:
            self.assertIsInstance(line, list)
            for param in line:
                self.assertIsInstance(param, str)

    def test_LargeOneLine_RandomSeperator(self):
        maxParamSize = 10
        size = (100, 2)
        sep = randomSymbols()
        bigString = ""
        for indexX, i in enumerate(range(size[0])):
            for index, x in enumerate(range(size[1])):
                bigString += randomString(maxParamSize)
                if (index != size[1] - 1):
                    bigString += sep
            if (indexX != size[0] - 1):
                bigString += "\n"
        csv = parseCSV(bigString, sep=sep)

        # Check size
        self.assertTrue(len(csv) == size[0])
        self.assertTrue(len(csv[0]) == size[1])
        # Check csvlist structure
        self.assertIsInstance(csv, list)
        for line in csv:
            self.assertIsInstance(line, list)
            for param in line:
                self.assertIsInstance(param, str)


class Request_Tests(unittest.TestCase):
    
    def verifyStatusCode(self, responsesList: list[Response] = None, response: Response = None, maxCode=399):
        """Check if responses in responseList, or Response have statusCode under maxCode.

        Args:
            responsesList (list[Response], optional (kinda)): List of responses from MakeRequests to verify.
            response (Response, optional): Response value to verify.
            maxCode (int, optional): Code to <= against. Defaults to 399.
            
            ik im bad at docstrings -_-
        """        
        if responsesList:
            for res in responsesList:
                self.assertTrue(res.status_code <= maxCode)
        if response:
            self.assertTrue(response.status_code <= maxCode)
        if not response and responsesList:
            print("Test: verifyStatusCode() No response or ResponseList given.")
            self.assertTrue(False)
            # Assert False because there are no Responses to check
        
    
    def test_Get_Empty(self):
        request = Request(reqtype="get", uri="https://httpbin.org/get")
        responses = MakeRequests(requestList=[request], dataList=[[""]])
        for response in responses:
            # Get values in common
            sameValues = (request.headers.items() & response.headers.items())
            for v in sameValues:
                self.assertEqual(request.headers[v], response.headers[v])
            # Check return value
            self.verifyStatusCode(response=response)
        
    
    def test_Post_3_Values_3_Lines(self):
        # Post Request Result Page \/
        resultsAt = "http://ptsv2.com/t/wdr4p-1625102266"
        lines = 3
        valuesPerLine = 3
        valuemaxlen = 5
        
        request = Request(reqtype="post", uri="http://ptsv2.com/t/wdr4p-1625102266/post?valueZero={0}?valueTwo={1}?valueTwo={2}")
        postData=[]
        for lines in range(lines):
            Line = []
            Line = [Line.append(randomString(valuemaxlen)) for x in range(valuesPerLine)]
        
        responses = MakeRequests(requestList=[request], dataList=postData)
        self.verifyStatusCode(responsesList=responses)
        
        resultsPage = BeautifulSoup(requests.get(resultsAt).text)
        # resultsPage.
        
        


if __name__ == "__main__":
    unittest.main()
