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
        with SavHeaderReader('../test_data/spssio_test.sav') as header:
            self.metadata = header.dataDictionary(True)

    def test_alignments(self):
        alignments = {'AGE2': 'right',
                      'AGE3': 'right',
                      'Age': 'left',
                      'AvgIncome': 'right',
                      'DATE_': 'left',
                      'ID': 'left',
                      'Income1': 'right',
                      'Income2': 'right',
                      'Income3': 'center',
                      'MONTH_': 'right',
                      'MaxIncome': 'right',
                      'QUARTER_': 'right',
                      'Region': 'left',
                      'SEX': 'right',
                      'V1': 'right',
                      'V2': 'right',
                      'V3': 'right',
                      'YEAR_': 'right',
                      'aLongStringVar': 'left',
                      'aShortStringVar': 'left',
                      'someDate': 'right',
                      'weightVar': 'right'}
        self.assertEqual(self.metadata.alignments, alignments)

    def test_caseWeightVar(self):
        self.assertEqual(self.metadata.caseWeightVar, 'weightVar')

    def test_columnWidths(self):
        columnWidths = {'AGE2': 10,
                        'AGE3': 10,
                        'Age': 10,
                        'AvgIncome': 11,
                        'DATE_': 10,
                        'ID': 10,
                        'Income1': 14,
                        'Income2': 14,
                        'Income3': 15,
                        'MONTH_': 8,
                        'MaxIncome': 11,
                        'QUARTER_': 10,
                        'Region': 10,
                        'SEX': 10,
                        'V1': 10,
                        'V2': 10,
                        'V3': 10,
                        'YEAR_': 10,
                        'aLongStringVar': 26,
                        'aShortStringVar': 17,
                        'someDate': 13,
                        'weightVar': 11}
        self.assertEqual(self.metadata.columnWidths, columnWidths)

    def test_fileAttributes(self):
        fileAttributes = {'$VariableView2[01]': 'name',
                          '$VariableView2[02]': 'type',
                          '$VariableView2[03]': 'width',
                          '$VariableView2[04]': 'decimals',
                          '$VariableView2[05]': 'label',
                          '$VariableView2[06]': 'values',
                          '$VariableView2[07]': 'missing',
                          '$VariableView2[08]': 'columns',
                          '$VariableView2[09]': 'alignment',
                          '$VariableView2[10]': 'measure',
                          '$VariableView2[11]': 'role',
                          '$VariableView2[12]': '@Formula',
                          '$VariableView2[13]': '@DerivedFrom',
                          '$VariableView2[14]': '@Notes',
                          'VersionNumber': '1'}
        self.assertEqual(self.metadata.fileAttributes, fileAttributes)

    def test_fileLabel(self):
        self.assertEqual(self.metadata.fileLabel, 'This is a file label')

    def test_formats(self):
        formats = {'AGE2': 'F8.2',
                   'AGE3': 'F8.2',
                   'Age': 'F3',
                   'AvgIncome': 'F8.2',
                   'DATE_': 'A8',
                   'ID': 'N6',
                   'Income1': 'F8.2',
                   'Income2': 'F8.2',
                   'Income3': 'F8.2',
                   'MONTH_': 'F2',
                   'MaxIncome': 'F8.2',
                   'QUARTER_': 'F1',
                   'Region': 'F8.2',
                   'SEX': 'F8.2',
                   'V1': 'F8.2',
                   'V2': 'F8.2',
                   'V3': 'F8.2',
                   'YEAR_': 'F8',
                   'aLongStringVar': 'A100',
                   'aShortStringVar': 'A1',
                   'someDate': 'ADATE40',
                   'weightVar': 'F8.2'}
        self.assertEqual(self.metadata.formats, formats)

    def test_measureLevels(self):
        measureLevels = {'AGE2': 'ratio',
                         'AGE3': 'ratio',
                         'Age': 'ratio',
                         'AvgIncome': 'ratio',
                         'DATE_': 'nominal',
                         'ID': 'nominal',
                         'Income1': 'ratio',
                         'Income2': 'ratio',
                         'Income3': 'ratio',
                         'MONTH_': 'ordinal',
                         'MaxIncome': 'ratio',
                         'QUARTER_': 'ordinal',
                         'Region': 'nominal',
                         'SEX': 'nominal',
                         'V1': 'nominal',
                         'V2': 'nominal',
                         'V3': 'nominal',
                         'YEAR_': 'ordinal',
                         'aLongStringVar': 'nominal',
                         'aShortStringVar': 'nominal',
                         'someDate': 'ratio',
                         'weightVar': 'nominal'}
        self.assertEqual(self.metadata.measureLevels, measureLevels)

    @unittest.skip("===========> CHECK THIS LATER!")
    def test_missingValues(self):
        sysmis = -1 * sys.float_info.max
        missingValues = {'AGE2': {},
                         'AGE3': {},
                         'Age': {'lower': 0.0, 'upper': 18.0},
                         'AvgIncome': {},
                         'DATE_': {},
                         'ID': {},
                         'Income1': {'lower': sysmis, 'upper': -1.0},
                         'Income2': {'lower': sysmis, 'upper': -1.0, 'value': 999.0},
                         'Income3': {'values': [999.0, 888.0, 777.0]},
                         'MONTH_': {},
                         'MaxIncome': {},
                         'QUARTER_': {},
                         'Region': {},
                         'SEX': {},
                         'V1': {},
                         'V2': {},
                         'V3': {},
                         'YEAR_': {},
                         'aLongStringVar': {},
                         'aShortStringVar': {'values': ['x', 'y']},
                         'someDate': {},
                         'weightVar': {}}
        miss = self.metadata.missingValues
        self.assertAlmostEqual(miss["Income1"]["lower"], sysmis)
        self.assertAlmostEqual(miss["Income2"]["lower"], sysmis)

        del miss["Income1"]["lower"]
        del miss["Income2"]["lower"]
        del missingValues["Income1"]["lower"]
        del missingValues["Income2"]["lower"]
        self.assertEqual(self.metadata.missingValues, missingValues)

    def test_multRespDefs(self):
        multRespDefs = {'V': {'countedValue': '1',
                              'label': '',
                              'setType': 'D',
                              'varNames': ['V1', 'V2', 'V3']},
                        'ages': {'label': 'the ages',
                                 'setType': 'C',
                                 'varNames': ['Age', 'AGE2', 'AGE3']},
                        'incomes': {'label': 'three kinds of income',
                                    'setType': 'C',
                                    'varNames': ['Income1',
                                                 'Income2',
                                                 'Income3',
                                                 'Age',
                                                 'AGE2',
                                                 'AGE3']}}
        self.assertEqual(self.metadata.multRespDefs, multRespDefs)

    def test_valueLabels(self):
        valueLabels = {'Age': {27.0: '27 y.o. ', 34.0: '34 y.o.', 50.0: '50 y.o.'},
                       'aShortStringVar': {'x': 'someValue label'}}
        self.assertEqual(self.metadata.valueLabels, valueLabels)

    def test_varAttributes(self):
        varAttributes = {'AvgIncome': {'DerivedFrom[1]': 'Income1',
                                       'DerivedFrom[2]': 'Income2',
                                       'DerivedFrom[3]': 'Income3',
                                       'Formula': 'mean(Income1, Income2, Income3)'},
                         'MaxIncome': {'DerivedFrom[1]': 'Income1',
                                       'DerivedFrom[2]': 'Income2',
                                       'DerivedFrom[3]': 'Income3',
                                       'Formula': 'max(Income1, Income2, Income3)'}}
        self.assertEqual(self.metadata.varAttributes, varAttributes)

    def test_varLabels(self):
        varLabels = {'AGE2': '',
                     'AGE3': '',
                     'Age': 'How old are you?',
                     'AvgIncome': '',
                     'DATE_': 'Date.  Format:  "MMM YYYY"              ',
                     'ID': '',
                     'Income1': '',
                     'Income2': '',
                     'Income3': '',
                     'MONTH_': 'MONTH, period 12',
                     'MaxIncome': '',
                     'QUARTER_': 'QUARTER, period 4',
                     'Region': 'What region do you live',
                     'SEX': '',
                     'V1': '',
                     'V2': '',
                     'V3': '',
                     'YEAR_': 'YEAR, not periodic',
                     'aLongStringVar': 'Some mysterious long stringVar',
                     'aShortStringVar': 'Some mysterious short stringVar',
                     'someDate': '',
                     'weightVar': ''}
        self.assertEqual(self.metadata.varLabels, varLabels)

    def test_varNames(self):
        varNames = ['ID',
                    'Age',
                    'Region',
                    'Income1',
                    'Income2',
                    'Income3',
                    'AvgIncome',
                    'MaxIncome',
                    'AGE2',
                    'AGE3',
                    'SEX',
                    'V1',
                    'V2',
                    'V3',
                    'someDate',
                    'aShortStringVar',
                    'aLongStringVar',
                    'weightVar',
                    'YEAR_',
                    'QUARTER_',
                    'MONTH_',
                    'DATE_']
        self.assertEqual(self.metadata.varNames, varNames)

    def test_varRoles(self):
        varRoles = {'AGE2': 'input',
                    'AGE3': 'input',
                    'Age': 'input',
                    'AvgIncome': 'input',
                    'DATE_': 'input',
                    'ID': 'input',
                    'Income1': 'target',
                    'Income2': 'target',
                    'Income3': 'target',
                    'MONTH_': 'input',
                    'MaxIncome': 'input',
                    'QUARTER_': 'input',
                    'Region': 'partition',
                    'SEX': 'input',
                    'V1': 'input',
                    'V2': 'input',
                    'V3': 'input',
                    'YEAR_': 'input',
                    'aLongStringVar': 'input',
                    'aShortStringVar': 'input',
                    'someDate': 'input',
                    'weightVar': 'input'}
        self.assertEqual(self.metadata.varRoles, varRoles)

    def test_varSets(self):
        self.assertEqual(self.metadata.varSets, {})

    def test_varTypes(self):
        varTypes = {'AGE2': 0,
                    'AGE3': 0,
                    'Age': 0,
                    'AvgIncome': 0,
                    'DATE_': 8,
                    'ID': 0,
                    'Income1': 0,
                    'Income2': 0,
                    'Income3': 0,
                    'MONTH_': 0,
                    'MaxIncome': 0,
                    'QUARTER_': 0,
                    'Region': 0,
                    'SEX': 0,
                    'V1': 0,
                    'V2': 0,
                    'V3': 0,
                    'YEAR_': 0,
                    'aLongStringVar': 100,
                    'aShortStringVar': 1,
                    'someDate': 0,
                    'weightVar': 0}
        self.assertEqual(self.metadata.varTypes, varTypes)

if __name__ == "__main__":
    unittest.main()