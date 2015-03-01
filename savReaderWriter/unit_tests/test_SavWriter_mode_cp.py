#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Use a nested context manager and mode="cp"
##############################################################################

import unittest
import os
import tempfile
import sys
from savReaderWriter import *

meta_expected = """\
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
salbegin -- 0"""

# This test passes the second time it is run. 
class test_SavWriter_copy_metadata(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.savFileName = "../test_data/Employee data.sav"
        self.savFileName1 = os.path.join(tempfile.gettempdir(), "test1.sav")
        self.savFileName2 = os.path.join(tempfile.gettempdir(), "test2.sav")

    #@unittest.skipIf(sys.version_info[0] > 2, "keywords must be string")
    @unittest.skip("Gives error 'Permission denied: '/tmp/test1.sav'")
    def test_SavWriter_copy_meta_dict(self):
        """Copy header info from one file to another (Method #1)"""
        # Python 3: self._setMissingValue(varName, **kwargs)
        # TypeError: _setMissingValue() keywords must be string
        # keywords like 'values', 'lower' and 'upper' may not be bytes.
        with SavHeaderReader(self.savFileName) as header:
            metadata = header.dataDictionary()
        with SavReader(self.savFileName) as reader:
            with SavWriter(self.savFileName1, **metadata) as writer:
                for line in reader:
                    writer.writerow(line)
        try:
            #os.remove(self.savFileName1)
            pass
        except:
            pass

    @unittest.skip("This is not working properly. File not properly closed?")
    def test_SavWriter_copy_meta_cp(self):
        """Copy header info from one file to another, mode 'cp' (Method #2)"""
        ## Uses <refSavFileName> as a donor file to initialize the header
        ## This will also copy DATE/TREND info, which is not copied using Method #1
        data = SavReader(self.savFileName, rawMode=True)
        with data: 
            varNames, varTypes = data.getSavFileInfo()[2:4]
            records = data.all()
        with SavWriter(self.savFileName2, varNames, varTypes,
                       refSavFileName=self.savFileName,
                       mode=b"cp") as writer:
            writer.writerows(records)

        savFileExists = os.path.exists(self.savFileName2) and \
                        os.path.getsize(self.savFileName2)
        self.assertTrue(savFileExists)

    @unittest.skip("This is not working properly. File not properly closed?")
    def test_SavWriter_check_copied_data_cp(self):
        # read the data back in to see if it looks the same
        records_got = []
        with SavReader(self.savFileName2, returnHeader=True) as reader:
            for lino, line in enumerate(reader):
                records_got.append(line)
                if lino > 2:
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

    @unittest.skip("This is not working properly. File not properly closed?")
    def test_SavWriter_check_copied_meta_cp(self):
        """read the meta data back in to see if it looks the same"""
        with SavHeaderReader(self.savFileName2) as header:
            self.assertEqual(meta_expected, str(header))
        try:
            #os.remove(self.savFileName2)
            pass
        except:
            pass

if __name__ == "__main__":
    unittest.main()









