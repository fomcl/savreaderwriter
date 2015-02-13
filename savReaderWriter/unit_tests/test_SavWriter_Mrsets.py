#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
from savReaderWriter import SavWriter


# TODO: tests for ioUtf8=True
# See also issue #26
records = [[1000, b"higher"], [2000, b"university"], 
           [2000, b"\xe5\xa4\xa7\xe5\xad\xa6 (chinese university)"]]

savFileName = os.path.join(tempfile.gettempdir(), "mrdefs_test.sav")
varNames = [b"income", b"educ"]
varTypes = {b"income": 0, b"educ": 30}

categorical =  {b"setType": b"C", 
                b"label": b"labelC",
                b"varNames": [b"salary", b"educ"]}
dichotomous = {b"setType": b"D", b"label": b"labelD",
                b"varNames": [b"salary", b"educ"], 
                b"countedValue": b"Yes"}
multRespDefs = {b"testSetC": categorical, 
                b"testSetD1": dichotomous}
#multRespDefs = {b"testSetD1": dichotomous1}
#multRespDefs = {b"testSetC": categorical} 

class Test_Mrsets(unittest.TestCase):

    """
    Write multiple response sets (dichotomy and categorical;
    extended ones can't be written, only read)
    """  

    def setUp(self):
        self.kwargs = dict(savFileName=savFileName, 
                           varNames=varNames, 
                           varTypes=varTypes)

    def test_multRespDefs_dichotomy(self):
        self.kwargs.update(dict(multRespDefs={b"testSetD1": dichotomous}))
        with SavWriter(**self.kwargs) as writer:
            writer.writerows(records)

    def test_multRespDefs_categorical(self):
        self.kwargs.update(dict(multRespDefs={b"testSetD1": categorical}))
        with SavWriter(**self.kwargs) as writer:
            writer.writerows(records)

    def test_multRespDefs_both(self):
        self.kwargs.update(dict(multRespDefs={b"testSetC": categorical, 
                                              b"testSetD1": dichotomous}))
        with SavWriter(**self.kwargs) as writer:
            writer.writerows(records)

    def tearDown(self):
        try:
            os.remove(savFileName)
        except:
            pass 

if __name__ == "__main__":
    unittest.main()

