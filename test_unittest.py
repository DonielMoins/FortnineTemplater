from typing import List
import unittest
from utils.general import parseCSV, randomString

class Test_CSVTests(unittest.TestCase):
    def testLargeOneLine(self):
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
        baseList = list(list(str()))
        self.assertTrue(isinstance(csv, type(baseList)))
        
if __name__ == "__main__":
    unittest.main()