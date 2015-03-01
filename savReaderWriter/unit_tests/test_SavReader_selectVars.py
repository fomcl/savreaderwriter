#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Read a select of variables from a file (see issue # 18)
##############################################################################

import unittest
from savReaderWriter import *


class test_SavReader_selectVars(unittest.TestCase):
    """Read a selection of a file"""

    def setUp(self):
        self.savFileName = "test_data/Employee data.sav"

    def test_SavReader_selectVars_one(self):
        """Read a selection of a file (one var)"""
        records_got = []
        with SavReader(self.savFileName, selectVars=[b'id'], 
                       returnHeader=True) as reader:
            for i, record in enumerate(reader):
                records_got.append(record)
                if i > 2:
                    break
        records_expected = [[b'id'], [1.0], [2.0], [3.0]]
        self.assertEqual(records_expected, records_got)

    def test_SavReader_selectVars_two(self):
        """Read a selection of a file (two vars)"""
        records_got = []
        with SavReader(self.savFileName, selectVars=[b'id', b'bdate'],
                       returnHeader=True) as reader:
            for i, record in enumerate(reader):
                records_got.append(record)
                if i > 2:
                    break
        records_expected = [[b'id', b'bdate'],
                            [1.0, b'1952-02-03'],
                            [2.0, b'1958-05-23'],
                            [3.0, b'1929-07-26']]
        self.assertEqual(records_expected, records_got)

if __name__ == "__main__":
    unittest.main()
