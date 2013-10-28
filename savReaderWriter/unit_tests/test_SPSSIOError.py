#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Check if the custom error class does its job
##############################################################################

import unittest
import os
import tempfile
import sys
import codecs
import savReaderWriter as rw

class test_SPSSIOError(unittest.TestCase):

    def setUp(self):
        self.badSavFile = os.path.join(tempfile.gettempdir(), "error.sav")
        with codecs.open(self.badSavFile, "wb", encoding="cp1252") as f:
            line = 79 * "*" + "\n"
            for i in range(100):
                f.write(line)

    def test_raises_SPSSIOError(self):
        module = rw if sys.version_info[0] > 2 else rw.error
        SPSSIOError = module.SPSSIOError  
        retcodes = module.retcodes
        with self.assertRaises(SPSSIOError):
            with rw.SavReader(self.badSavFile) as reader:
                for line in reader:
                    pass
            error = sys.exc_info()[1]
            self.assertEqual(retcodes.get(error.retcode), "SPSS_INVALID_FILE")
  
    def tearDown(self):
        try:
            os.remove(self.badSavFile)
        except:
            pass

if __name__ == "__main__":
    unittest.main()


