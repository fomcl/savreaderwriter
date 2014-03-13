#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
from savReaderWriter import *

##############################################################################
## Write a file, incl. SPSS date values
##############################################################################

# var1 is a 5-char string var, the others are numerical:
# formats, varLabels, valueLabels, missingValues etc. may also be None (default).
# This also shows how date fields can be converted into spss dates.
# Spss dates are *stored* as the number of seconds since Oct 14, 1582, but
# *displayed* as <format>. In this case they are displayed as EDATE
# (European date, cf. ADATE = American date), ie. as dd.mm.yyyy


class test_SavWriter_date(unittest.TestCase):

    def setUp(self):
        self.savFileName = os.path.join(tempfile.gettempdir(), 'test.sav')

    def test_SavWriter_date(self):
        records = [[b'Test1', 1, 1, b'2010-08-11'], 
                   [b'Test2', 2, 1, b'1910-01-12']]
        varNames = [b'var1', b'v2', b'v3', b'bdate']
        varTypes = {b'var1': 41, b'v2': 0, b'v3': 0, b'bdate': 0}
        formats = {b'var1': b'A41', b'v2': b'F3.1', 
                   b'v3': b'F5.1', b'bdate': b'EDATE40'}
        missingValues = {b'var1': {b'values': [b'Test1', b'Test2']},
                         b'v2': {b'values': 1}}
        varLabels = {b'var1': b'This is variable 1',
                     b'v2': b'This is v2!',
                     b'bdate': b'dob'}
        valueLabels = {b'var1': {b'Test1': b'Test1 value label',
                                 b'Test2': b'Test2 value label'},
                       b'v2': {1: b'yes', 2: b'no'}}
        with SavWriter(self.savFileName, varNames, varTypes,
                       valueLabels, varLabels, formats) as writer:
            pos = varNames.index(b'bdate')
            for record in records:
                record[pos] = writer.spssDateTime(record[pos], '%Y-%m-%d')
                writer.writerow(record)

        # read it back in in rawMode (dates not converted to ISO-dates)
        reader = None
        try:
            reader = SavReader(self.savFileName, rawMode=True) 
            records_got = reader.all()
        finally:
            if reader is not None:
                reader.close()
        value1 = b'Test1                                           '
        value2 = b'Test2                                           ' 
        records_expected = [[value1, 1, 1, 13500864000.0],
                            [value2, 2, 1, 10326873600.0]]
        self.assertEqual(records_expected, records_got)

    def tearDown(self):
        try:
            os.remove(self.savFileName)
        except:
            pass 

if __name__ == "__main__":
    unittest.main()

