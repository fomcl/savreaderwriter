#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Read a file and get some basic file info (reports)
##############################################################################

import unittest
import sys
import gocept.testing.assertion
from savReaderWriter import *

report_expected = """\
**********************************************************************
*File '../savReaderWriter/test_data/Employee data.sav' (24.32 kB) has 10 columns (variables) and 474 rows (4740 values)
*The file was created with SPSS version: MS Windows Release 11.0 spssio32.dll (11.1.0)
*The interface locale is: '...'
*The interface mode is: Codepage (...)
*The file encoding is: 'utf_8' (Code page: 65001)
*File encoding and the interface encoding are compatible: ...
*Your computer's locale is: '...' (Code page: ...)
*The file contains the following variables:
  01. id (F4 - numerical)
  02. gender (A1 - string)
  03. bdate (ADATE10 - numerical)
  04. educ (F2 - numerical)
  05. jobcat (F1 - numerical)
  06. salary (DOLLAR8 - numerical)
  07. salbegin (DOLLAR8 - numerical)
  08. jobtime (F2 - numerical)
  09. prevexp (F6 - numerical)
  10. minority (F1 - numerical)
**********************************************************************
"""

class test_SavReader_file_report(unittest.TestCase, gocept.testing.assertion.Ellipsis):
    """Generate a file report"""

    def setUp(self):
        self.savFileName = "../savReaderWriter/test_data/Employee data.sav"

    def test_SavReader_report_python2_and_3_str(self):
        data = SavReader(self.savFileName)
        with data:
            report_got = str(data)
        self.assertEllipsis(report_expected, report_got)

    @unittest.skipIf(sys.version_info[0] > 2, "No 'unicode' in Python 3")
    def test_SavReader_report_python2_unicode(self):
        data = SavReader(self.savFileName)
        with data:
            report_got = unicode(data)
            encoding = data.fileEncoding
        self.assertEllipsis(report_expected.decode(encoding), report_got)

    @unittest.skipIf(sys.version_info[0] == 2, "No bytes method in Python 2")
    def test_SavReader_report_python3_bytes(self):
        data = SavReader(self.savFileName)
        with data:
            encoding = data.fileEncoding
            report_got = bytes(data, encoding)
        self.assertEllipsis(report_expected.encode(encoding), report_got)

if __name__ == "__main__":
    unittest.main()
