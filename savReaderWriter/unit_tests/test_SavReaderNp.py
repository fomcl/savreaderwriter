#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import numpy as np
import datetime
from savReaderNp import *

class Test_SavReaderNp(unittest.TestCase):

    def setUp(self):
        self.filename = "./test_data/Employee data.sav"

    def test_getitem_indexing(self):
        self.npreader = SavReaderNp(self.filename)
        actual = self.npreader[0].tolist()
        desired = [(1.0, 'm', datetime(1952, 2, 3, 0, 0), 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0)]
        self.assertEquals(actual, desired)

    def test_getitem_indexing_IndexError(self):
        self.npreader = SavReaderNp(self.filename)
        with self.assertRaises(IndexError):
            self.npreader[474]

    def test_getitem_indexing_raw(self):
        self.npreader = SavReaderNp(self.filename, rawMode=True)
        actual = self.npreader[0].tolist()
        desired = [(1.0, 'm       ', 11654150400.0, 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0)]
        self.assertEquals(actual, desired)

    def test_getitem_slicing(self):
        self.npreader = SavReaderNp(self.filename)
        actual = self.npreader[0:2].tolist()
        desired = [(1.0, 'm', datetime(1952, 2, 3, 0, 0), 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0), 
                   (2.0, 'm', datetime(1958, 5, 23, 0, 0), 16.0, 1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0)]
        self.assertEquals(actual, desired)

    def test_getitem_indexing_IndexError(self):
        self.npreader = SavReaderNp(self.filename)
        self.assertEquals(self.npreader[475:666].tolist(), []) 

    def test_getitem_striding(self):
        self.npreader = SavReaderNp(self.filename)
        actual = self.npreader[3::-1].tolist()
        desired = [(4.0, 'f', datetime(1947, 4, 15, 0, 0), 8.0, 1.0, 21900.0, 13200.0, 98.0, 190.0, 0.0), 
                   (3.0, 'f', datetime(1929, 7, 26, 0, 0), 12.0, 1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0), 
                   (2.0, 'm', datetime(1958, 5, 23, 0, 0), 16.0, 1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0), 
                   (1.0, 'm', datetime(1952, 2, 3, 0, 0), 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0)]
        self.assertEquals(actual, desired)

    def tearDown(self):
        self.npreader.close()

if __name__ == "__main__":
    unittest.main()

