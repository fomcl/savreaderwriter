#!/usr/bin/env python
# -*- coding: utf-8 -*-


##############################################################################
## Use a nested context manager and mode="cp"
##############################################################################

import unittest
import os
import tempfile
from savReaderWriter import *

meta_expected = """\
#ALIGNMENTS
salary -- right
jobcat -- right
bdate -- right
minority -- right
prevexp -- right
gender -- left
salbegin -- right
jobtime -- right
educ -- right
id -- right
#CASEWEIGHTVAR
#COLUMNWIDTHS
salary -- 8
jobcat -- 8
bdate -- 13
minority -- 8
prevexp -- 8
gender -- 1
salbegin -- 8
jobtime -- 8
educ -- 8
id -- 8
#FILEATTRIBUTES
#FILELABEL
05.00.00
#FORMATS
salary -- DOLLAR8
jobcat -- F1
bdate -- ADATE10
minority -- F1
prevexp -- F6
gender -- A1
salbegin -- DOLLAR8
jobtime -- F2
educ -- F2
id -- F4
#MEASURELEVELS
salary -- ratio
jobcat -- ordinal
bdate -- ratio
minority -- ordinal
prevexp -- ratio
gender -- nominal
salbegin -- ratio
jobtime -- ratio
educ -- ordinal
id -- ratio
#MISSINGVALUES
salary: values -- 0.0
jobcat: values -- 0.0
minority: values -- 9.0
salbegin: values -- 0.0
jobtime: values -- 0.0
educ: values -- 0.0
#MULTRESPDEFS
#VALUELABELS
salary: 0.0 -- missing
jobcat: 0.0 -- 0 (Missing)
jobcat: 1.0 -- Clerical
jobcat: 2.0 -- Custodial
jobcat: 3.0 -- Manager
salbegin: 0.0 -- missing
minority: 0.0 -- No
minority: 1.0 -- Yes
minority: 9.0 -- 9 (Missing)
prevexp: 0.0 -- missing
gender: f -- Female
gender: m -- Male
jobtime: 0.0 -- missing
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
#VARATTRIBUTES
#VARLABELS
salary -- Current Salary
jobcat -- Employment Category
bdate -- Date of Birth
minority -- Minority Classification
prevexp -- Previous Experience (months)
gender -- Gender
salbegin -- Beginning Salary
jobtime -- Months since Hire
educ -- Educational Level (years)
id -- Employee Code
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
salary -- input
jobcat -- input
bdate -- input
minority -- input
prevexp -- input
gender -- input
salbegin -- input
jobtime -- input
educ -- input
id -- input
#VARSETS
SALARY -- salbegin, salary
DEMOGR -- gender, minority, educ
#VARTYPES
salary -- 0
jobcat -- 0
bdate -- 0
minority -- 0
prevexp -- 0
gender -- 1
salbegin -- 0
jobtime -- 0
educ -- 0
id -- 0"""

 
class test_SavWriter_copy_metadata(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.savFileName = "../savReaderWriter/test_data/Employee data.sav"
        self.savFileName1 = os.path.join(tempfile.gettempdir(), "test1.sav")
        self.savFileName2 = os.path.join(tempfile.gettempdir(), "test2.sav")

    def test_SavWriter_copy_meta_dict(self):
        """Copy header info from one file to another (Method #1)"""
        with SavHeaderReader(self.savFileName) as header:
            metadata = header.dataDictionary() 
        with SavReader(self.savFileName) as reader:
            with SavWriter(self.savFileName1, **metadata) as writer:
                for line in reader:
                    writer.writerow(line)

    def test_SavWriter_copy_meta_cp(self):
        """Copy header info from one file to another, mode 'cp' (Method #2)"""
        ## Uses <refSavFileName> as a donor file to initialize the header
        ## This will also copy DATE/TREND info, which is not copied using Method #1
        data = SavReader(self.savFileName, rawMode=True)
        with data: 
            varNames, varTypes = data.getSavFileInfo()[2:4]
            with SavWriter(self.savFileName2, varNames, varTypes,
                           refSavFileName=self.savFileName,
                           mode="cp") as writer:
                for line in iter(data):
                    writer.writerow(line)

        # read the data back in to see if it looks the same
        records_got = []
        with SavReader(self.savFileName2, returnHeader=True) as reader:
            for lino, line in enumerate(reader):
                records_got.append(line)
                if lino > 3:
                    break

        records_expected = \
        [[b'id', b'gender', b'bdate', b'educ', b'jobcat',b'salary',
          b'salbegin', b'jobtime', b'prevexp', b'minority'],
         [1.0, b'm', b'1952-02-03', 15.0, 3.0, 
          57000.0, 27000.0, 98.0, 144.0, 0.0],
         [2.0, b'm', b'1958-05-23', 16.0, 1.0,
          40200.0, 18750.0, 98.0, 36.0, 0.0],
         [3.0, b'f', b'1929-07-26', 12.0, 1.0,
          21450.0, 12000.0, 98.0, 381.0, 0.0]]
        self.assertEqual(records_expected, records_got)

    def test_SavWriter_check_meta_cp(self):
        """read the meta data back in to see if it looks the same"""
        with SavHeaderReader(self.savFileName2) as header:
            self.assertEqual(meta_expected, str(header))

    def tearDown(self):
        try:
            os.remove(self.savFileName1)
            os.remove(self.savFileName2)
        except:
            pass

if __name__ == "__main__":
    unittest.main()









