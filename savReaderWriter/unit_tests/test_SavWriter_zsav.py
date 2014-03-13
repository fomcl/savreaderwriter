#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Write a file using zlib compression (.zsav)
##############################################################################

import unittest
import os
import tempfile
from savReaderWriter import *

# .zsav = zlib compressed (requires IO libraries >= v21)
# .zsav files CANNOT be read using SPSS v20 or lower
class test_SavWriter_zsav(unittest.TestCase):
    """Write a file using zlib compression (.zsav)"""

    def setUp(self):
        self.savFileName =  os.path.join(tempfile.gettempdir(), "test.zsav")
        varNames = ['var1', 'v2', 'v3', 'bdate']
        varTypes = {'var1': 6, 'v2': 0, 'v3': 0, 'bdate': 10}
        self.args = (self.savFileName, varNames, varTypes)

    def test_SavWriter_typical(self):
        records_in = [[b'Test1', 1, 1, b'2010-08-11'],
                      [b'Test2', 2, 1, b'1910-01-12']]
        with SavWriter(*self.args) as writer:
            for record in records_in:
                writer.writerow(record)

        reader = SavReader(self.savFileName)
        with reader:  
            records_out = [line for line in iter(reader)]
            compression_got = reader.fileCompression
        self.assertEqual(records_in, records_out)
        self.assertEqual(b"zlib", compression_got)

    def tearDown(self):
        os.remove(self.savFileName)

if __name__ == "__main__":
    unittest.main()
