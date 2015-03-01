#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
from savReaderWriter import *


class test_SavHeaderReader_dataDictionary_namedtuple(unittest.TestCase):
    """ Tests whether dataDictionary method correctly returns self.metadata
    as a namedtuple (asNamedtuple=True)
    """
    def setUp(self):
        self.maxDiff = None
        with SavHeaderReader('test_data/spssio_test.sav') as header:
            self.metadata = header.dataDictionary(True)

    def test_alignments(self):
        alignments = {b'AGE2': b'right',
                      b'AGE3': b'right',
                      b'Age': b'left',
                      b'AvgIncome': b'right',
                      b'DATE_': b'left',
                      b'ID': b'left',
                      b'Income1': b'right',
                      b'Income2': b'right',
                      b'Income3': b'center',
                      b'MONTH_': b'right',
                      b'MaxIncome': b'right',
                      b'QUARTER_': b'right',
                      b'Region': b'left',
                      b'SEX': b'right',
                      b'V1': b'right',
                      b'V2': b'right',
                      b'V3': b'right',
                      b'YEAR_': b'right',
                      b'aLongStringVar': b'left',
                      b'aShortStringVar': b'left',
                      b'someDate': b'right',
                      b'weightVar': b'right'}
        self.assertEqual(self.metadata.alignments, alignments)

    def test_caseWeightVar(self):
        self.assertEqual(self.metadata.caseWeightVar, b'weightVar')

    def test_columnWidths(self):
        columnWidths = {b'AGE2': 10,
                        b'AGE3': 10,
                        b'Age': 10,
                        b'AvgIncome': 11,
                        b'DATE_': 10,
                        b'ID': 10,
                        b'Income1': 14,
                        b'Income2': 14,
                        b'Income3': 15,
                        b'MONTH_': 8,
                        b'MaxIncome': 11,
                        b'QUARTER_': 10,
                        b'Region': 10,
                        b'SEX': 10,
                        b'V1': 10,
                        b'V2': 10,
                        b'V3': 10,
                        b'YEAR_': 10,
                        b'aLongStringVar': 26,
                        b'aShortStringVar': 17,
                        b'someDate': 13,
                        b'weightVar': 11}
        self.assertEqual(self.metadata.columnWidths, columnWidths)

    def test_fileAttributes(self):
        fileAttributes = {b'$VariableView2[01]': b'name',
                          b'$VariableView2[02]': b'type',
                          b'$VariableView2[03]': b'width',
                          b'$VariableView2[04]': b'decimals',
                          b'$VariableView2[05]': b'label',
                          b'$VariableView2[06]': b'values',
                          b'$VariableView2[07]': b'missing',
                          b'$VariableView2[08]': b'columns',
                          b'$VariableView2[09]': b'alignment',
                          b'$VariableView2[10]': b'measure',
                          b'$VariableView2[11]': b'role',
                          b'$VariableView2[12]': b'@Formula',
                          b'$VariableView2[13]': b'@DerivedFrom',
                          b'$VariableView2[14]': b'@Notes',
                          b'VersionNumber': b'1'}
        self.assertEqual(self.metadata.fileAttributes, fileAttributes)

    def test_fileLabel(self):
        self.assertEqual(self.metadata.fileLabel, b'This is a file label')

    def test_formats(self):
        formats = {b'AGE2': b'F8.2',
                   b'AGE3': b'F8.2',
                   b'Age': b'F3',
                   b'AvgIncome': b'F8.2',
                   b'DATE_': b'A8',
                   b'ID': b'N6',
                   b'Income1': b'F8.2',
                   b'Income2': b'F8.2',
                   b'Income3': b'F8.2',
                   b'MONTH_': b'F2',
                   b'MaxIncome': b'F8.2',
                   b'QUARTER_': b'F1',
                   b'Region': b'F8.2',
                   b'SEX': b'F8.2',
                   b'V1': b'F8.2',
                   b'V2': b'F8.2',
                   b'V3': b'F8.2',
                   b'YEAR_': b'F8',
                   b'aLongStringVar': b'A100',
                   b'aShortStringVar': b'A1',
                   b'someDate': b'ADATE40',
                   b'weightVar': b'F8.2'}
        self.assertEqual(self.metadata.formats, formats)

    def test_measureLevels(self):
        measureLevels = {b'AGE2': b'ratio',
                         b'AGE3': b'ratio',
                         b'Age': b'ratio',
                         b'AvgIncome': b'ratio',
                         b'DATE_': b'nominal',
                         b'ID': b'nominal',
                         b'Income1': b'ratio',
                         b'Income2': b'ratio',
                         b'Income3': b'ratio',
                         b'MONTH_': b'ordinal',
                         b'MaxIncome': b'ratio',
                         b'QUARTER_': b'ordinal',
                         b'Region': b'nominal',
                         b'SEX': b'nominal',
                         b'V1': b'nominal',
                         b'V2': b'nominal',
                         b'V3': b'nominal',
                         b'YEAR_': b'ordinal',
                         b'aLongStringVar': b'nominal',
                         b'aShortStringVar': b'nominal',
                         b'someDate': b'ratio',
                         b'weightVar': b'nominal'}
        self.assertEqual(self.metadata.measureLevels, measureLevels)

    def test_missingValues(self):
        sysmis = -1 * sys.float_info.max
        missingValues = {b'AGE2': {},
                         b'AGE3': {},
                         b'Age': {'lower': 0.0, 'upper': 18.0},
                         b'AvgIncome': {},
                         b'DATE_': {},
                         b'ID': {},
                         b'Income1': {'lower': sysmis, 'upper': -1.0},
                         b'Income2': {'lower': sysmis, 'upper': -1.0, 'value': 999.0},
                         b'Income3': {'values': [999.0, 888.0, 777.0]},
                         b'MONTH_': {},
                         b'MaxIncome': {},
                         b'QUARTER_': {},
                         b'Region': {},
                         b'SEX': {},
                         b'V1': {},
                         b'V2': {},
                         b'V3': {},
                         b'YEAR_': {},
                         b'aLongStringVar': {},
                         b'aShortStringVar': {'values': [b'x', b'y']},
                         b'someDate': {},
                         b'weightVar': {}}
        miss = self.metadata.missingValues
        A_VERY_SMALL_NUMBER = 10 ** -50
        self.assertTrue(miss[b"Income1"]["lower"] < A_VERY_SMALL_NUMBER)
        self.assertTrue(miss[b"Income2"]["lower"] < A_VERY_SMALL_NUMBER)

        del miss[b"Income1"]["lower"]
        del miss[b"Income2"]["lower"]
        del missingValues[b"Income1"]["lower"]
        del missingValues[b"Income2"]["lower"]
        self.assertEqual(self.metadata.missingValues, missingValues)

    def test_multRespDefs(self):
        multRespDefs = {b'V': {b'countedValue': b'1',
                              b'label': b'',
                              b'setType': b'D',
                              b'varNames': [b'V1', b'V2', b'V3']},
                        b'ages': {b'label': b'the ages',
                                 b'setType': b'C',
                                 b'varNames': [b'Age', b'AGE2', b'AGE3']},
                        b'incomes': {b'label': b'three kinds of income',
                                    b'setType': b'C',
                                    b'varNames': [b'Income1',
                                                 b'Income2',
                                                 b'Income3',
                                                 b'Age',
                                                 b'AGE2',
                                                 b'AGE3']}}
        self.assertEqual(self.metadata.multRespDefs, multRespDefs)

    def test_valueLabels(self):
        valueLabels = {b'Age': {27.0: b'27 y.o. ', 34.0: b'34 y.o.', 50.0: b'50 y.o.'},
                       b'aShortStringVar': {b'x': b'someValue label'}}
        self.assertEqual(self.metadata.valueLabels, valueLabels)

    def test_varAttributes(self):
        varAttributes = {b'AvgIncome': {b'DerivedFrom[1]': b'Income1',
                                        b'DerivedFrom[2]': b'Income2',
                                        b'DerivedFrom[3]': b'Income3',
                                        b'Formula': b'mean(Income1, Income2, Income3)'},
                         b'MaxIncome': {b'DerivedFrom[1]': b'Income1',
                                        b'DerivedFrom[2]': b'Income2',
                                        b'DerivedFrom[3]': b'Income3',
                                        b'Formula': b'max(Income1, Income2, Income3)'}}
        self.assertEqual(self.metadata.varAttributes, varAttributes)

    def test_varLabels(self):
        varLabels = {b'AGE2': b'',
                     b'AGE3': b'',
                     b'Age': b'How old are you?',
                     b'AvgIncome': b'',
                     b'DATE_': b'Date.  Format:  "MMM YYYY"              ',
                     b'ID': b'',
                     b'Income1': b'',
                     b'Income2': b'',
                     b'Income3': b'',
                     b'MONTH_': b'MONTH, period 12',
                     b'MaxIncome': b'',
                     b'QUARTER_': b'QUARTER, period 4',
                     b'Region': b'What region do you live',
                     b'SEX': b'',
                     b'V1': b'',
                     b'V2': b'',
                     b'V3': b'',
                     b'YEAR_': b'YEAR, not periodic',
                     b'aLongStringVar': b'Some mysterious long stringVar',
                     b'aShortStringVar': b'Some mysterious short stringVar',
                     b'someDate': b'',
                     b'weightVar': b''}
        self.assertEqual(self.metadata.varLabels, varLabels)

    def test_varNames(self):
        varNames = [b'ID',
                    b'Age',
                    b'Region',
                    b'Income1',
                    b'Income2',
                    b'Income3',
                    b'AvgIncome',
                    b'MaxIncome',
                    b'AGE2',
                    b'AGE3',
                    b'SEX',
                    b'V1',
                    b'V2',
                    b'V3',
                    b'someDate',
                    b'aShortStringVar',
                    b'aLongStringVar',
                    b'weightVar',
                    b'YEAR_',
                    b'QUARTER_',
                    b'MONTH_',
                    b'DATE_']
        self.assertEqual(self.metadata.varNames, varNames)

    def test_varRoles(self):
        varRoles = {b'AGE2': b'input',
                    b'AGE3': b'input',
                    b'Age': b'input',
                    b'AvgIncome': b'input',
                    b'DATE_': b'input',
                    b'ID': b'input',
                    b'Income1': b'target',
                    b'Income2': b'target',
                    b'Income3': b'target',
                    b'MONTH_': b'input',
                    b'MaxIncome': b'input',
                    b'QUARTER_': b'input',
                    b'Region': b'partition',
                    b'SEX': b'input',
                    b'V1': b'input',
                    b'V2': b'input',
                    b'V3': b'input',
                    b'YEAR_': b'input',
                    b'aLongStringVar': b'input',
                    b'aShortStringVar': b'input',
                    b'someDate': b'input',
                    b'weightVar': b'input'}
        self.assertEqual(self.metadata.varRoles, varRoles)

    def test_varSets(self):
        self.assertEqual(self.metadata.varSets, {})

    def test_varTypes(self):
        varTypes = {b'AGE2': 0,
                    b'AGE3': 0,
                    b'Age': 0,
                    b'AvgIncome': 0,
                    b'DATE_': 8,
                    b'ID': 0,
                    b'Income1': 0,
                    b'Income2': 0,
                    b'Income3': 0,
                    b'MONTH_': 0,
                    b'MaxIncome': 0,
                    b'QUARTER_': 0,
                    b'Region': 0,
                    b'SEX': 0,
                    b'V1': 0,
                    b'V2': 0,
                    b'V3': 0,
                    b'YEAR_': 0,
                    b'aLongStringVar': 100,
                    b'aShortStringVar': 1,
                    b'someDate': 0,
                    b'weightVar': 0}
        self.assertEqual(self.metadata.varTypes, varTypes)

if __name__ == "__main__":
    unittest.main()
