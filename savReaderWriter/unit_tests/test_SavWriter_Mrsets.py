#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
import copy
from savReaderWriter import *

# See also issue #26
savFileName = os.path.join(tempfile.gettempdir(), "mrdefs_test.sav")
varNames = [b"income", b"educ"]
varTypes = {b"income": 0, b"educ": 30}
records = [[1000, b"higher"], [2000, b"university"], 
           [2000, b"\xe5\xa4\xa7\xe5\xad\xa6 (chinese university)"]]

class Test_Mrsets(unittest.TestCase):

    """
    Write multiple response sets (dichotomy and categorical;
    extended ones can't be written, only read)
    """  

    def setUp(self):
        self.categorical = {b"label": b"\xe5\xa4\xa7\xe5\xad\xa6 (labelC)",
                            b"setType": b"C", 
                            b"varNames": [b"income", b"educ"]}
        self.dichotomous = {b"countedValue": b"Yes",
                            b"label": b"labelD",
                            b"setType": b"D", 
                            b"varNames": [b"income", b"educ"]}
        self.multRespDefs = {b"testSetC": self.categorical, 
                             b"testSetD": self.dichotomous}
        self.kwargs = dict(savFileName=savFileName, 
                           varNames=varNames, 
                           varTypes=varTypes)
        self.maxDiff = None

    def test_multRespDefs_dichotomy(self):
        multRespDefs = {b"testSetD": copy.deepcopy(self.dichotomous)} 
        self.kwargs.update(dict(multRespDefs=multRespDefs))
        with SavWriter(**self.kwargs) as writer:
            writer.writerows(records)
        with SavHeaderReader(savFileName) as header:
            actual = header.multRespDefs
        desired = {b"testSetD": self.multRespDefs[b"testSetD"]}
        self.assertEqual(desired, actual)

    def test_multRespDefs_categorical(self):
        multRespDefs = {b"testSetC": copy.deepcopy(self.categorical)}
        self.kwargs.update(dict(multRespDefs=multRespDefs))
        with SavWriter(**self.kwargs) as writer:
            writer.writerows(records)
        with SavHeaderReader(savFileName) as header:
            actual = header.multRespDefs
        desired = {b"testSetC": self.multRespDefs[b"testSetC"]}
        self.assertEqual(desired, actual)

    def test_multRespDefs_both(self):
        multRespDefs = copy.deepcopy(self.multRespDefs) 
        self.kwargs.update(dict(multRespDefs=multRespDefs))
        with SavWriter(**self.kwargs) as writer:
            writer.writerows(records)
        with SavHeaderReader(savFileName) as header:
            actual = header.multRespDefs
        desired = self.multRespDefs
        self.assertEqual(desired, actual)

    def test_multRespDefs_unicode_both(self):
        multRespDefs = copy.deepcopy(self.multRespDefs) 
        self.kwargs.update(dict(multRespDefs=multRespDefs, ioUtf8=True))
        with SavWriter(**self.kwargs) as writer:
            for record in records:
                urecord = [item.decode("utf-8") if hasattr(item, "decode")
                           else item for item in record]
                writer.writerow(urecord)
        with SavHeaderReader(savFileName, ioUtf8=True) as header:
            actual = header.multRespDefs
        # Python 3: returned as <map object> --> turn into list
        varNamesC = list(actual[u'testSetC'][u'varNames']) 
        varNamesD = list(actual[u'testSetD'][u'varNames'])
        actual[u'testSetC'][u'varNames'] = varNamesC
        actual[u'testSetD'][u'varNames'] = varNamesD
        desired = \
        {u'testSetC': {u'label': u'\u5927\u5b66 (labelC)',
                       u'setType': u'C',
                       u'varNames': [u'income', u'educ']},
         u'testSetD': {u'countedValue': u'Yes',
                       u'label': u'labelD',
                       u'setType': u'D',
                       u'varNames': [u'income', u'educ']}}
        self.assertEqual(desired, actual)

    def tearDown(self):
        try:
            os.remove(savFileName)
        except:
            pass 

if __name__ == "__main__":
    unittest.main()

