#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Write a file, typical use
##############################################################################

import unittest
import os
import tempfile
from savReaderWriter import *

class test_SavWriter_typical_use(unittest.TestCase):
    """ Write a file, typical use"""

    def setUp(self):
        self.savFileName =  os.path.join(tempfile.gettempdir(), "test.sav")
        varNames = ['var1', 'v2', 'v3', 'bdate']
        varTypes = {'var1': 6, 'v2': 0, 'v3': 0, 'bdate': 10}
        self.args = (self.savFileName, varNames, varTypes)

    def test_SavWriter_typical(self):
        records_in = [[b'Test1', 1, 1, b'2010-08-11'],
                      [b'Test2', 2, 1, b'1910-01-12']]
        with SavWriter(*self.args) as writer:
            for record in records_in:
                writer.writerow(record)

        with SavReader(self.savFileName) as reader:
            records_out = [line for line in iter(reader)]

        self.assertEqual(records_in, records_out)

    def tearDown(self):
        os.remove(self.savFileName)

if __name__ == "__main__":
    unittest.main()
