#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Check if the custom error class does its job
##############################################################################

import unittest
import os
import sys
import warnings
import savReaderWriter as rw

warnings_are_ignored = os.getenv("PYTHONWARNINGS") == "ignore"

class test_SPSSIOWarning(unittest.TestCase):

    def setUp(self):
        self.savFileName = "../savReaderWriter/test_data/Employee data.sav"
        os.environ["SAVRW_DISPLAY_WARNS"] = "always"

    # I have no idea why this works differently in Python 2
    @unittest.skipIf(sys.version_info[0] < 3, "Python 2: Warnings different?")
    @unittest.skipIf(warnings_are_ignored, "Warnings are ignored")
    def test_raises_SPSSIOWarning(self):
        module = rw if sys.version_info[0] > 2 else rw.error
        SPSSIOWarning = module.SPSSIOWarning  
        #with self.assertRaises(SPSSIOWarning) as e:
        with warnings.catch_warnings(record=True) as w:
            with rw.SavHeaderReader(self.savFileName) as header:
                metadata = str(header)
                self.assertTrue(issubclass(w[-1].category, UserWarning))
                self.assertTrue("SPSS_NO_CASEWGT" in str(w[-1].message))
  
    def tearDown(self):
        try:
            del os.environ["SAVRW_DISPLAY_WARNS"]
        except:
            pass

if __name__ == "__main__":
    unittest.main()


