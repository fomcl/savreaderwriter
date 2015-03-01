#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Print a report of the header information
##############################################################################

import unittest
import sys
import os
from savReaderWriter import *

report_expected = """\
#ALIGNMENTS
bdate -- right
educ -- right
gender -- left
id -- right
jobcat -- right
jobtime -- right
minority -- right
prevexp -- right
salary -- right
salbegin -- right
#CASEWEIGHTVAR
#COLUMNWIDTHS
bdate -- 13
educ -- 8
gender -- 1
id -- 8
jobcat -- 8
jobtime -- 8
minority -- 8
prevexp -- 8
salary -- 8
salbegin -- 8
#FILEATTRIBUTES
#FILELABEL
05.00.00
#FORMATS
bdate -- ADATE10
educ -- F2
gender -- A1
id -- F4
jobcat -- F1
jobtime -- F2
minority -- F1
prevexp -- F6
salary -- DOLLAR8
salbegin -- DOLLAR8
#MEASURELEVELS
bdate -- ratio
educ -- ordinal
gender -- nominal
id -- ratio
jobcat -- ordinal
jobtime -- ratio
minority -- ordinal
prevexp -- ratio
salary -- ratio
salbegin -- ratio
#MISSINGVALUES
educ: values -- 0.0
jobcat: values -- 0.0
jobtime: values -- 0.0
minority: values -- 9.0
salary: values -- 0.0
salbegin: values -- 0.0
#MULTRESPDEFS
#VALUELABELS
educ: 0.0 -- 0 (Missing)
educ: 8.0 -- 8
educ: 12.0 -- 12
educ: 14.0 -- 14
educ: 15.0 -- 15
educ: 16.0 -- 16
educ: 17.0 -- 17
educ: 18.0 -- 18
educ: 19.0 -- 19
educ: 20.0 -- 20
educ: 21.0 -- 21
gender: f -- Female
gender: m -- Male
jobcat: 0.0 -- 0 (Missing)
jobcat: 1.0 -- Clerical
jobcat: 2.0 -- Custodial
jobcat: 3.0 -- Manager
jobtime: 0.0 -- missing
minority: 0.0 -- No
minority: 1.0 -- Yes
minority: 9.0 -- 9 (Missing)
prevexp: 0.0 -- missing
salary: 0.0 -- missing
salbegin: 0.0 -- missing
#VARATTRIBUTES
#VARLABELS
bdate -- Date of Birth
educ -- Educational Level (years)
gender -- Gender
id -- Employee Code
jobcat -- Employment Category
jobtime -- Months since Hire
minority -- Minority Classification
prevexp -- Previous Experience (months)
salary -- Current Salary
salbegin -- Beginning Salary
#VARNAMES
id
gender
bdate
educ
jobcat
salary
salbegin
jobtime
prevexp
minority
#VARROLES
bdate -- input
educ -- input
gender -- input
id -- input
jobcat -- input
jobtime -- input
minority -- input
prevexp -- input
salary -- input
salbegin -- input
#VARSETS
DEMOGR -- gender, minority, educ
SALARY -- salbegin, salary
#VARTYPES
bdate -- 0
educ -- 0
gender -- 1
id -- 0
jobcat -- 0
jobtime -- 0
minority -- 0
prevexp -- 0
salary -- 0
salbegin -- 0""".replace("\n", os.linesep)

report_expected_ioUtf8 = """\
File 'greetings.sav' built using SavReaderWriter.py version 3.1.1 (Thu Jan 17 16:35:14 2013)
#ALIGNMENTS
Bondjoû -- left
greeting -- left
line -- left
#CASEWEIGHTVAR
#COLUMNWIDTHS
Bondjoû -- 20
greeting -- 50
line -- 8
#FILEATTRIBUTES
#FILELABEL
File created by user 'Administrator' at Thu Jan 17 16:35:14 2013
#FORMATS
Bondjoû -- A20
greeting -- A50
line -- F8.2
#MEASURELEVELS
Bondjoû -- unknown
greeting -- unknown
line -- unknown
#MISSINGVALUES
Bondjoû: values -- ¡Hola! 
line: lower -- 0.0
line: upper -- 9.0
#MULTRESPDEFS
#VALUELABELS
Bondjoû: Thai                 -- สวัสดี
#VARATTRIBUTES
#VARLABELS
Bondjoû -- 
greeting -- السلام عليكم
line -- 
#VARNAMES
line
Bondjoû
greeting
#VARROLES
Bondjoû -- input
greeting -- input
line -- input
#VARSETS
#VARTYPES
Bondjoû -- 20
greeting -- 50
line -- 0""".replace("\n", os.linesep)

class test_SavHeaderReader_metadata_report(unittest.TestCase):
    """Generate a metadata report"""

    def setUp(self):
        #self.maxDiff = None
        self.savFileName = "../test_data/Employee data.sav"
        self.savFileName_ioUtf8 = "../test_data/greetings.sav"

    # __str__ (although the meaning is different in Python 2 and 3)
    def test_SavHeaderReader_report_python2_and_3_str(self):
        with SavHeaderReader(self.savFileName) as header:
            report_got = str(header)
        self.assertEqual(report_expected, report_got)

    def test_SavHeaderReader_report_python2_and_3_str_ioUtf8(self):
        with SavHeaderReader(self.savFileName_ioUtf8, ioUtf8=True) as header:
            report_got = str(header)
        self.assertEqual(report_expected_ioUtf8, report_got)

    # __unicode__
    @unittest.skipIf(sys.version_info[0] > 2, "No 'unicode' in Python 3")
    def test_SavHeaderReader_report_python2_unicode(self):
        with SavHeaderReader(self.savFileName) as header:
            encoding = header.fileEncoding
            report_got = unicode(header)
        self.assertEqual(report_expected.decode(encoding), report_got)

    @unittest.skipIf(sys.version_info[0] > 2, "No 'unicode' in Python 3")
    def test_SavHeaderReader_report_python2_unicode_ioUtf8(self):
        with SavHeaderReader(self.savFileName_ioUtf8, ioUtf8=True) as header:
            encoding = header.fileEncoding
            report_got = unicode(header)
        self.assertEqual(report_expected_ioUtf8.decode(encoding), report_got)

    # __bytes__
    @unittest.skipIf(sys.version_info[0] == 2, "No bytes method in Python 2")
    def test_SavHReader_report_python3_bytes(self):
        with SavHeaderReader(self.savFileName) as header:
            encoding = header.fileEncoding
            report_got = bytes(header, encoding)
        self.assertEqual(report_expected.encode(encoding), report_got)

    @unittest.skipIf(sys.version_info[0] == 2, "No bytes method in Python 2")
    def test_SavHReader_report_python3_bytes_ioUtf8(self):
        with SavHeaderReader(self.savFileName_ioUtf8, ioUtf8=True) as header:
            encoding = header.fileEncoding
            report_got = bytes(header, encoding)
        self.assertEqual(report_expected_ioUtf8.encode(encoding), report_got)

if __name__ == "__main__":
    unittest.main()

