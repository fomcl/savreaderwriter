#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Read a file containg all the supported date formats
##############################################################################

import unittest
import os
import tempfile
import sys
from savReaderWriter import *

records_expected = \
    [[b'2010-08-11 00:00:00', b'32 WK 2010', b'2010-08-11', b'3 Q 2010', 
      b'2010-08-11', b'2010-08-11', b'11 00:00:00', b'2010-08-11', b'August',
      b'August 2010', b'00:00:00.000000', b'2010-08-11', b'Wednesday'],
     [b'1910-01-12 00:00:00', b'02 WK 1910', b'1910-01-12', b'1 Q 1910', 
      b'1910-01-12', b'1910-01-12', b'12 00:00:00', b'1910-01-12', b'January', 
      b'January 1910', b'00:00:00.000000', b'1910-01-12', b'Wednesday'],
     [None, None, None, None, None, None, None, 
      None, None, None, None, None, None],
     [None, None, None, None, None, None, None, 
      None, None, None, None, None, None]]

# This test passes the second time it is run. 
class test_SavWriter_dates_elaborate(unittest.TestCase):

    def setUp(self):
        ## first, create a test file
        self.maxDiff = None
        self.savFileName = os.path.join(tempfile.gettempdir(), "test_dates.sav")
        varNames = [b'var_datetime', b'var_wkyr', b'var_date', b'var_qyr', b'var_edate',
                    b'var_sdate', b'var_dtime', b'var_jdate', b'var_month', b'var_moyr',
                    b'var_time', b'var_adate', b'var_wkday']
        varTypes = {v : 0 for v in varNames}
        spssfmts = [b'DATETIME40', b'WKYR10', b'DATE10', b'QYR10', b'EDATE10',
                    b'SDATE10', b'DTIME10', b'JDATE10', b'MONTH10', b'MOYR10',
                    b'TIME10', b'ADATE10', b'WKDAY10']
        formats = dict(zip(varNames, spssfmts))
        records = [[b'2010-08-11'] * len(varNames), [b'1910-01-12'] * len(varNames),
                   [b''] * len(varNames), [None] * len(varNames)]

        with SavWriter(self.savFileName, varNames, varTypes, formats=formats) as writer:
            for record in records:
                for pos, value in enumerate(record):
                    record[pos] = writer.spssDateTime(record[pos], "%Y-%m-%d")
                writer.writerow(record)

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









