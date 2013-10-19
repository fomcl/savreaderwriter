#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Read a file and iterate over its records (.zsav)
##############################################################################
## It's a good idea not to change the .zsav extension
## SPSS versions 20 or older are NOT compatible with zsav
## As of Oct 2013, the latest SPSS version is 22, so older versions are pretty
## common!

import unittest
from savReaderWriter import *

test1 = b'Test1                                                   '
test2 = b'Test2                                                   '
records_expected = [[b'var1', b'var2', b'var3', b'bdate'],
                    [test1, 1.0, 1.0, b'2010-08-11      '],
                    [test2, 2.0, 1.0, b'1910-01-12      ']]

class test_SavReader_zsav(unittest.TestCase):
    """ Read a .zsav file (zlib compression)"""

    def test_SavReader_zsavl(self):

        savFileName = "../savReaderWriter/test_data/zlib_compressed.zsav"
        records_got = []
        with SavReader(savFileName, returnHeader=True) as reader:
            for record in reader:
                records_got.append(record)

        self.assertEqual(records_expected, records_got)

if __name__ == "__main__":
    unittest.main()
