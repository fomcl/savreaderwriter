#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Write a file (elaborate example)
##############################################################################

import unittest
import tempfile
import os
import re
import sys
from savReaderWriter import *


class test_SavWriter_elaborate(unittest.TestCase):
    def setUp(self):
        self.savFileName = os.path.join(tempfile.gettempdir(), 'test.sav')

    def test_SavWriter_elaborate_writerows(self):
        varNames = [b'id', b'gender', b'bdate', b'educ', b'jobcat', b'salary',
                    b'salbegin', b'jobtime', b'prevexp', b'minority']
        varLabels = {b'gender': b'guys/gals'}
        valueLabels = {b"gender": {b"m": b"males", b"f": b"females"},
                       b"educ": {1: b"lower", 2: b"middle", 3: b"higher"}}
        varTypes = {b'salary': 0, b'jobcat': 0, b'bdate': 0, b'minority': 0,
                    b'prevexp': 0, b'gender': 1, b'salbegin': 0,
                    b'jobtime': 0, b'educ': 0, b'id': 0}
        formats = {b'salary': b'DOLLAR8', b'jobcat': b'F3',
                   b'bdate': b'ADATE40', b'minority': b'F3',
                   b'prevexp': b'F3', b'gender': b'A1',
                   b'salbegin': b'DOLLAR8', b'jobtime': b'F8',
                   b'educ': b'F3', b'id': b'N9'}
        varSets = {b'SALARY': [b'salbegin', b'salary'],
                   b'DEMOGR': [b'gender', b'minority', b'educ']}
        varRoles = {b'prevexp': b'input', b'gender': b'input',
                    b'jobtime': b'input', b'salbegin': b'input',
                    b'salary': b'input', b'id': b'input',
                    b'bdate': b'input', b'minority': b'input',
                    b'jobcat': b'input', b'educ': b'input'}
        varAttributes = {b'salary': {b'DemographicVars': b'1'},
                         b'jobcat': {b'DemographicVars': b'1'},
                         b'gender': {b'Binary': b'Yes'},
                         b'educ': {b'DemographicVars': b'1'}}
        fileAttributes = {b'TheDate[2]': b'10/21/2005',
                          b'RevisionDate[2]': b'10/21/2005',
                          b'RevisionDate[1]': b'10/29/2004'}
        # note that 'values' and other keywords must be strings!
        missingValues = {b'educ': {'values': [1, 2, 3]},
                         b'gender': {'values': b'x'}}
        kwargs = dict(savFileName = self.savFileName,
                      varNames = varNames,
                      varTypes = varTypes,
                      varLabels = varLabels,
                      valueLabels = valueLabels,
                      varSets = varSets,
                      varRoles = varRoles,
                      missingValues = missingValues,
                      varAttributes = varAttributes,
                      fileAttributes = fileAttributes)
        records = [[1.0, b'm       ', 11654150400.0, 15.0, 3.0,
                    57000.0, 27000.0, 98.0, 144.0, 0.0],
                   [2.0, b'm       ', 11852956800.0, 16.0, 1.0,
                    40200.0, 18750.0, 98.0, 36.0, 0.0]]
        with SavWriter(**kwargs) as writer:
            writer.writerows(records)


        ### read it back in
        reader = None
        try:
            reader = SavReader(self.savFileName, rawMode=True)
            records_got = [line for line in iter(reader)]
        finally:
            if reader is not None:
                reader.close()
        self.assertEqual(records_got, records)


        ### check the meta data.
        with SavHeaderReader(self.savFileName) as header:
            metadata = header.dataDictionary(True)

        # varNames
        expected = [b'id', b'gender', b'bdate', b'educ', b'jobcat',
                    b'salary', b'salbegin', b'jobtime', b'prevexp',
                    b'minority']
        self.assertEqual(getattr(metadata, 'varNames'), expected)

         # varTypes
        expected = {b'prevexp': 0, b'gender': 1, b'jobtime': 0,
                    b'salbegin': 0, b'salary': 0, b'id': 0,
                    b'bdate': 0, b'minority': 0, b'jobcat': 0,
                    b'educ': 0}
        self.assertEqual(getattr(metadata, 'varTypes'), expected)

        # valueLabels
        expected = {b'educ': {1.0: b'lower',
                              2.0: b'middle',
                              3.0: b'higher'},
                    b'gender': {b'f': b'females',
                                b'm': b'males'}}
        self.assertEqual(getattr(metadata, 'valueLabels'), expected)

        # varLabels
        expected = {b'prevexp': b'', b'gender': b'guys/gals',
                    b'jobtime': b'', b'salbegin': b'', b'salary': b'',
                    b'id': b'', b'bdate': b'', b'minority': b'',
                    b'jobcat': b'', b'educ': b''}
        self.assertEqual(getattr(metadata, 'varLabels'), expected)

        # formats
        expected = {b'prevexp': b'F8.2', b'gender': b'A1',
                    b'jobtime': b'F8.2', b'salbegin': b'F8.2',
                    b'salary': b'F8.2', b'id': b'F8.2',
                    b'bdate': b'F8.2', b'minority': b'F8.2',
                    b'jobcat': b'F8.2', b'educ': b'F8.2'}
        self.assertEqual(getattr(metadata, 'formats'), expected)

        # missingValues
        expected = {b'prevexp': {}, b'gender': {'values': [b'x']},
                    b'jobtime': {}, b'salbegin': {},
                    b'salary': {}, b'id': {}, b'bdate': {},
                    b'minority': {}, b'jobcat': {},
                    b'educ': {'values': [1.0, 2.0, 3.0]}}
        self.assertEqual(getattr(metadata, 'missingValues'), expected)

        # measurelevels
        expected = {b'prevexp': b'unknown', b'gender': b'unknown',
                    b'jobtime': b'unknown', b'salbegin': b'unknown',
                    b'salary': b'unknown', b'id': b'unknown',
                    b'bdate': b'unknown', b'minority': b'unknown',
                    b'jobcat': b'unknown', b'educ': b'unknown'}
        self.assertEqual(getattr(metadata, 'measureLevels'), expected)

        # columnwidths
        expected = {b'prevexp': 8, b'gender': 10, b'jobtime': 8,
                    b'salbegin': 8, b'salary': 8, b'id': 8,
                    b'bdate': 8, b'minority': 8, b'jobcat': 8,
                    b'educ': 8}
        self.assertEqual(getattr(metadata, 'columnWidths'), expected)

        # alignments
        expected = {b'prevexp': b'left', b'gender': b'left',
                    b'jobtime': b'left', b'salbegin': b'left',
                    b'salary': b'left', b'id': b'left',
                    b'bdate': b'left', b'minority': b'left',
                    b'jobcat': b'left', b'educ': b'left'}
        self.assertEqual(getattr(metadata, 'alignments'), expected)

        # varSets
        expected = {b'DEMOGR': [b'gender', b'minority', b'educ'],
                    b'SALARY': [b'salbegin', b'salary']}
        self.assertEqual(getattr(metadata, 'varSets'), expected)

        # varRoles
        expected = {b'prevexp': b'input', b'gender': b'input',
                    b'jobtime': b'input', b'salbegin': b'input',
                    b'salary': b'input', b'id': b'input',
                    b'bdate': b'input', b'minority': b'input',
                    b'jobcat': b'input', b'educ': b'input'}
        self.assertEqual(getattr(metadata, 'varRoles'), expected)

        # varAttributes
        expected = {b'jobcat': {b'DemographicVars': b'1'},
                    b'salary': {b'DemographicVars': b'1'},
                    b'gender': {b'Binary': b'Yes'},
                    b'educ': {b'DemographicVars': b'1'}}
        self.assertEqual(getattr(metadata, 'varAttributes'), expected)

        # fileAttributes
        expected = {b'RevisionDate[1]': b'10/29/2004',
                    b'RevisionDate[2]': b'10/21/2005',
                    b'TheDate[2]': b'10/21/2005'}
        self.assertEqual(getattr(metadata, 'fileAttributes'), expected)

        # fileLabel
        regex = (b"File created by user '\w+' at \w+ \w+ "
                 b" ?\d+ \d+:\d+:\d+ \d{4}")
        m = re.match(regex,getattr(metadata, 'fileLabel'), re.I)
        self.assertTrue(bool(m))

        # multRespDefs
        self.assertEqual(getattr(metadata, 'multRespDefs'), {})

        # caseWeightVar
        self.assertEqual(getattr(metadata, 'caseWeightVar'), b'')


    def tearDown(self):
        try:
            os.remove(self.savFileName)
        except:
            pass


if __name__ == "__main__":
    unittest.main()

