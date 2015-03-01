#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Read a file and use __len__, __getitem__
##############################################################################

import unittest
import sys

try:
    import numpy
    numpyOK = True
except ImportError:
    numpyOK = False

from savReaderWriter import *
from py3k import *

class test_SavReader_utilities(unittest.TestCase):
    """Read a file and use __len__, __getitem__"""

    def setUp(self):
        self.savFileName = "test_data/Employee data.sav"
        self.data = SavReader(self.savFileName)

    def test_SavReader_len(self):
        """Read a file, get number of cases using __len__"""
        nrows_got = len(self.data)
        self.assertEqual(474, nrows_got)

    def test_SavReader_shape(self):
        """Read a file, retrieve its dimensions (nrows, ncols)"""
        dimensions = self.data.shape
        self.assertEqual(474, dimensions.nrows)
        self.assertEqual(10, dimensions.ncols)

    def test_SavReader_indexing(self):
        """Read a file, use indexing (__getitem__)"""
        records_expected = \
        [[1.0, b'm', b'1952-02-03', 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0],
         [2.0, b'm', b'1958-05-23', 16.0, 1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0],
         [3.0, b'f', b'1929-07-26', 12.0, 1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0],
         [4.0, b'f', b'1947-04-15', 8.0, 1.0, 21900.0, 13200.0, 98.0, 190.0, 0.0],
         [5.0, b'm', b'1955-02-09', 15.0, 1.0, 45000.0, 21000.0, 98.0, 138.0, 0.0],
         [6.0, b'm', b'1958-08-22', 15.0, 1.0, 32100.0, 13500.0, 98.0, 67.0, 0.0]]
        self.assertEqual(records_expected, self.data[:6])

        # head()
        records_expected = \
        [[1.0, b'm', b'1952-02-03', 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0], 
         [2.0, b'm', b'1958-05-23', 16.0, 1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0], 
         [3.0, b'f', b'1929-07-26', 12.0, 1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0], 
         [4.0, b'f', b'1947-04-15', 8.0, 1.0, 21900.0, 13200.0, 98.0, 190.0, 0.0], 
         [5.0, b'm', b'1955-02-09', 15.0, 1.0, 45000.0, 21000.0, 98.0, 138.0, 0.0]]
        self.assertEqual(records_expected, self.data.head())

        # tail() 
        records_expected = \
        [[471.0, b'm', b'1966-08-03', 15.0, 1.0, 26400.0, 15750.0, 64.0, 32.0, 1.0], 
         [472.0, b'm', b'1966-02-21', 15.0, 1.0, 39150.0, 15750.0, 63.0, 46.0, 0.0], 
         [473.0, b'f', b'1937-11-25', 12.0, 1.0, 21450.0, 12750.0, 63.0, 139.0, 0.0], 
         [474.0, b'f', b'1968-11-05', 12.0, 1.0, 29400.0, 14250.0, 63.0, 9.0, 0.0]]
        self.assertEqual(records_expected, self.data.tail(4))

        # IndexError, self.data[475] (the test file has 474 cases)
        self.assertRaises(IndexError, self.data.__getitem__, 475)

    def test_SavReader_slicing(self):
        """Read a file, use slicing (__getitem__)"""
        records_expected = \
        [1.0, b'm', b'1952-02-03', 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0]
        self.assertEqual(records_expected, self.data[0])

    def test_SavReader_striding(self):
        """Read a file, use striding (__getitem__)."""
        records_expected = \
        [[474.0, b'f', b'1968-11-05', 12.0, 1.0, 29400.0, 14250.0, 63.0, 9.0, 0.0], 
         [473.0, b'f', b'1937-11-25', 12.0, 1.0, 21450.0, 12750.0, 63.0, 139.0, 0.0], 
         [472.0, b'm', b'1966-02-21', 15.0, 1.0, 39150.0, 15750.0, 63.0, 46.0, 0.0], 
         [471.0, b'm', b'1966-08-03', 15.0, 1.0, 26400.0, 15750.0, 64.0, 32.0, 1.0], 
         [470.0, b'm', b'1964-01-22', 12.0, 1.0, 26250.0, 15750.0, 64.0, 69.0, 1.0]] 
        records_expected.extend(
        [[5.0, b'm', b'1955-02-09', 15.0, 1.0, 45000.0, 21000.0, 98.0, 138.0, 0.0], 
         [4.0, b'f', b'1947-04-15', 8.0, 1.0, 21900.0, 13200.0, 98.0, 190.0, 0.0], 
         [3.0, b'f', b'1929-07-26', 12.0, 1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0], 
         [2.0, b'm', b'1958-05-23', 16.0, 1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0], 
         [1.0, b'm', b'1952-02-03', 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0]])
        reversed_records = self.data[::-1]
        records_got = reversed_records[:5] + reversed_records[-5:]
        self.assertEqual(records_expected, records_got)

    def test_SavReader_more_striding(self):
       """Return the even records using striding"""
       records_expected = \
        [[1.0, b'm', b'1952-02-03', 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0],
         [3.0, b'f', b'1929-07-26', 12.0, 1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0],
         [5.0, b'm', b'1955-02-09', 15.0, 1.0, 45000.0, 21000.0, 98.0, 138.0, 0.0]]
       records_got = self.data[::2]
       self.assertEqual(records_expected, records_got[:3])

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_slicing_1(self):
        records_expected = [[5.0, b'm', b'1955-02-09'],
                            [6.0, b'm', b'1958-08-22']]
        records_got = self.data[4:6, :3]  # Row 4 & 5, first three cols
        self.assertEqual(records_expected, records_got)

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_slicing_2(self):
        records_expected = [[1.0, b'm', b'1952-02-03'],
                            [2.0, b'm', b'1958-05-23'],
                            [3.0, b'f', b'1929-07-26'],
                            [472.0, b'm', b'1966-02-21'],
                            [473.0, b'f', b'1937-11-25'],
                            [474.0, b'f', b'1968-11-05']]
        records_got = self.data[..., :3]  # all rows of first three cols
        self.assertTrue(len(records_got) == 474)

        records_got = records_got[:3] + records_got[-3:]
        self.assertEqual(records_expected, records_got)

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_slicing_3(self):
        records_expected = [[1.0, b'm', b'1952-02-03', 15.0, 3.0, 
                             57000.0, 27000.0, 98.0, 144.0, 0.0],
                            [2.0, b'm', b'1958-05-23', 16.0, 1.0, 
                             40200.0, 18750.0, 98.0, 36.0, 0.0],
                            [3.0, b'f', b'1929-07-26', 12.0, 1.0, 
                             21450.0, 12000.0, 98.0, 381.0, 0.0]]
        records_got = self.data[:3, ...]  # all cols of first three rows
        self.assertEqual(records_expected, records_got)

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_indexing_1(self):
        records_expected = list(map(float, range(1, 475)))
        records_got = self.data[..., 0]  # First column
        self.assertEqual(records_expected, records_got)

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_indexing_2(self):
        records_expected = [1.0, b'm', b'1952-02-03', 15.0, 3.0,
                            57000.0, 27000.0, 98.0, 144.0, 0.0]
        records_got = self.data[0, ...]  # First row
        self.assertEqual(records_expected, records_got)

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_indexing_3(self):
        records_expected = [1.0]
        records_got = self.data[0, 0]  # First value
        self.assertEqual(records_expected, records_got)

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_both_1(self):
        records_expected = [1.0, 2.0]
        records_got = self.data[:2, 0]  # First two values of first col
        self.assertEqual(records_expected, records_got)

    @unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
    def test_SavReader_array_slicing_both_2(self):
        records_expected = [1.0, b'm']
        records_got = self.data[0, :2]  # First two values of first row
        self.assertEqual(records_expected, records_got)

    def test_SavReader_get(self):
        """Read a file and do a binary search for records (get)"""
        try:
            reader = SavReader(self.savFileName, idVar=b"id")

            # get first record where id==4
            records_expected = [4.0, b'f', b'1947-04-15', 8.0, 1.0,
                                21900.0, 13200.0, 98.0, 190.0, 0.0]
            self.assertEqual(records_expected, reader.get(4, "not found"))

            # gets all records where id==4
            records_expected = [[4.0, b'f', b'1947-04-15', 8.0, 1.0,
                                 21900.0, 13200.0, 98.0, 190.0, 0.0]]
            self.assertEqual(records_expected, reader.get(4, "not found", full=True))

            # some more checks 
            records_expected = [474.0, b'f', b'1968-11-05', 12.0, 1.0,
                                29400.0, 14250.0, 63.0, 9.0, 0.0]
            self.assertEqual(records_expected, reader.get(474, "not found"))
            self.assertEqual("not found", reader.get(475, "not found"))
            self.assertEqual("not found", reader.get(666, "not found"))

        finally:
            reader.close()

    def tearDown(self):
        self.data.close()

if __name__ == "__main__":
    unittest.main()
