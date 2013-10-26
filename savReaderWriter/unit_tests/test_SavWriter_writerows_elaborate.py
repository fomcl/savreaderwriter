#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Write a file (elaborate example)
##############################################################################

import unittest
import tempfile
import os
from savReaderWriter import *

class test_SavWriter_elaborate(unittest.TestCase):

    def setUp(self):
        self.savFileName = os.path.join(tempfile.gettempdir(), 'test.sav')

    def test_SavWriter_elaborate_writerows(self):
        varNames = [b'id', b'gender', b'bdate', b'educ', b'jobcat', b'salary',
                    b'salbegin', b'jobtime', b'prevexp', b'minority']
        varLabels = {b'gender': b'guys/gals'}
        varTypes = {b'salary': 0, b'jobcat': 0, b'bdate': 0, b'minority': 0,
                    b'prevexp': 0, b'gender': 1, b'salbegin': 0,
                    b'jobtime': 0, b'educ': 0, b'id': 0}
        formats = {b'salary': b'DOLLAR8', b'jobcat': b'F3', b'bdate': b'ADATE40',
                   b'minority': b'F3', b'prevexp': b'F3', b'gender': b'A1',
                   b'salbegin': b'DOLLAR8', b'jobtime': b'F8', b'educ': b'F3',
                   b'id': b'N9'}
        varSets = {b'SALARY': [b'salbegin', b'salary'],
                   b'DEMOGR': [b'gender', b'minority', b'educ']}
        varAttributes = {b'salary': {b'DemographicVars': b'1'},
                         b'jobcat': {b'DemographicVars': b'1'},
                         b'gender': {b'Binary': b'Yes'},
                         b'educ': {b'DemographicVars': b'1'}}
        fileAttributes = {b'TheDate[2]': b'10/21/2005',
                          b'RevisionDate[2]': b'10/21/2005',
                          b'RevisionDate[1]': '10/29/2004'}
        missingValues = {b'educ': {b'values': [1, 2, 3]}, b'gender': {b'values': b'x'}}
        records = [[1.0, b'm       ', 11654150400.0, 15.0, 3.0,
                    57000.0, 27000.0, 98.0, 144.0, 0.0],
                   [2.0, b'm       ', 11852956800.0, 16.0, 1.0,
                    40200.0, 18750.0, 98.0, 36.0, 0.0]]
        with SavWriter(self.savFileName, varNames, varTypes,
                       varLabels=varLabels, varSets=varSets,
                       missingValues=missingValues, varAttributes=varAttributes,
                       fileAttributes=fileAttributes) as writer:
            writer.writerows(records)

        # read it back in 
        reader = None
        try:
            reader = SavReader(self.savFileName, rawMode=True)
            records_got = [line for line in iter(reader)]
        finally:
            if reader is not None:
                reader.close()
        self.assertEqual(records_got, records)

    def tearDown(self):
        try:
            os.remove(self.savFileName)
        except:
            pass 

if __name__ == "__main__":
    unittest.main()

