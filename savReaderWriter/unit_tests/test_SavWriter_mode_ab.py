#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Append some records to an existing file, using mode="ab"
##############################################################################

import unittest
import shutil
import tempfile
import os
from savReaderWriter import *
 
class test_SavWriter_append_data(unittest.TestCase):

    def setUp(self):
        self.savFileName = "test_data/Employee data.sav"
        self.savFileNameCopy = os.path.join(tempfile.gettempdir(), "test.sav")
        shutil.copy(self.savFileName, self.savFileNameCopy)
        reader = None
        try:
            reader = SavReader(self.savFileName, rawMode=True)
            self.NROWS_ORIGINAL = len(reader)
            self.varNames, self.varTypes = reader.getSavFileInfo()[2:4]
        finally:
            if reader is not None:
                reader.close()

    def test_SavWriter_append_data(self):
        """Append 100 records to an existing file"""
        NROWS_EXTRA = 100
        line = [1.0, b'm', 11654150400.0, 15.0, 3.0, 
                57000.0, 27000.0, 98.0, 144.0, 0.0]
        with SavWriter(self.savFileNameCopy, self.varNames,
                       self.varTypes, mode=b"ab") as writer:
            for i in range(NROWS_EXTRA):
                writer.writerow(line)

        ## Demonstrate that the number of records has increased by 100.
        reader = None
        try:
            reader = SavReader(self.savFileNameCopy)
            n_records_got = len(reader)
        finally:
            if reader is not None:
                reader.close()
        self.assertEqual(n_records_got, self.NROWS_ORIGINAL + NROWS_EXTRA)

    def tearDown(self):
        try:
            os.remove(self.savFileNameCopy)
        except:
            pass

if __name__ == "__main__":
    unittest.main()

