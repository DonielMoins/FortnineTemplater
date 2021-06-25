from typing import List
import unittest
from utils.general import parseCSV, randomString, randomSymbols

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
        
        
if __name__ == "__main__":
    unittest.main()