#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Read a file containg all the supported date formats
##############################################################################

import unittest
import os
import tempfile
import sys
import functools
from time import strftime, strptime
from savReaderWriter import *

if sys.version_info[0] > 2:
    bytes = functools.partial(bytes, encoding='utf-8')

# make sure the test passes in other locales too
stamp  = lambda v, fmt: bytes(strftime(fmt, strptime(v, '%Y-%m-%d')))
wed1, august = stamp('2010-08-11', '%A'), stamp('2010-08-11', '%B')
wed2, january = stamp('1910-01-12', '%A'), stamp('1910-01-12', '%B')
records_expected = \
    [[b'2010-08-11 00:00:00', b'32 WK 2010', b'2010-08-11', b'3 Q 2010',
      b'2010-08-11', b'2010-08-11', b'11 00:00:00', b'2010-08-11', august,
      august + b' 2010', b'00:00:00.000000', b'2010-08-11', wed1],
     [b'1910-01-12 00:00:00', b'02 WK 1910', b'1910-01-12', b'1 Q 1910',
      b'1910-01-12', b'1910-01-12', b'12 00:00:00', b'1910-01-12', january,
      january + b' 1910', b'00:00:00.000000', b'1910-01-12', wed2],
     [None, None, None, None, None, None, None,
      None, None, None, None, None, None],
     [None, None, None, None, None, None, None,
      None, None, None, None, None, None]]

# PSPP does not know how to display all of these formats.
# DTIME is a strange format, SPSS does not display it properly (?).
# Incorrect in SPSS: compute x = date.dmy(01, 02, 2015); formats x (dtime10) 
class test_SavWriter_dates_elaborate(unittest.TestCase):

    def setUp(self):
        ## first, create a test file
        self.savFileName = os.path.join(tempfile.gettempdir(), "test_dates.sav")
        varNames = [b'var_datetime', b'var_wkyr', b'var_date', b'var_qyr', b'var_edate',
                    b'var_sdate', b'var_dtime', b'var_jdate', b'var_month', b'var_moyr',
                    b'var_time', b'var_adate', b'var_wkday']
        varTypes = {v : 0 for v in varNames}
        spssfmts = [b'DATETIME40', b'WKYR10', b'DATE10', b'QYR10', b'EDATE10',
                    b'SDATE10', b'DTIME10', b'JDATE10', b'MONTH10', b'MOYR10',
                    b'TIME10', b'ADATE10', b'WKDAY10']
        formats = dict(zip(varNames, spssfmts))
        records = [[b'2010-08-11' for v in varNames],
                   [b'1910-01-12' for v in varNames],
                   [b'' for v in varNames],
                   [None for v in varNames]]

        kwargs = dict(savFileName=self.savFileName, varNames=varNames,
                      varTypes=varTypes, formats=formats)
        with SavWriter(**kwargs) as writer:
            for i, record in enumerate(records):
                for pos, value in enumerate(record):
                    record[pos] = writer.spssDateTime(record[pos], "%Y-%m-%d")
                writer.writerow(record)
        
        self.maxDiff = None

    def test_dates(self):
        """Test if 13 different date/time formats are written and read 
        correctly"""
        data = SavReader(self.savFileName)
        with data:
            records_got = data.all()
        self.assertEqual(records_expected, records_got)

    def test_dates_recodeSysmisTo(self):
        """Test if recodeSysmisTo arg recodes missing date value"""
        data = SavReader(self.savFileName, recodeSysmisTo=999)
        with data:
            records_got = data.all()
        records_expected_999 = records_expected[:2] + 2 * [13 * [999]]
        self.assertEqual(records_expected_999, records_got)

    def tearDown(self):
        try:
            os.remove(self.savFileName)
        except:
            pass

if __name__ == "__main__":
    unittest.main()









