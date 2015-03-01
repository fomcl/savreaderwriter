#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Rich comparison operators
##############################################################################

import unittest
import sys
from savReaderWriter import *

class test_SavReader_typical_use(unittest.TestCase):
    """Rich comparison operators"""

    def setUp(self):
        savFileName = "test_data/german.sav"
        self.data = SavReader(savFileName)

    def test_rich_comp_eq(self):
        """testing operator =="""
        self.assertFalse(self.data == 3)
        self.assertFalse(self.data == 2)
        self.assertTrue(self.data == 1) 

    def test_rich_comp_ge(self):
        """testing operator >="""
        self.assertFalse(self.data >= 3)
        self.assertFalse(self.data >= 2)
        self.assertTrue(self.data >= 1)

    def test_rich_comp_le(self):
        """testing operator <="""
        self.assertTrue(self.data <= 3)
        self.assertTrue(self.data <= 2)
        self.assertTrue(self.data <= 1)

    def test_rich_comp_gt(self):
        """testing operator >"""
        self.assertFalse(self.data > 3)
        self.assertFalse(self.data > 2)
        self.assertFalse(self.data > 1)
    
    def test_rich_comp_lt(self):
        """testing operator <"""
        self.assertTrue(self.data < 3)
        self.assertTrue(self.data < 2)
        self.assertFalse(self.data < 1)

    def test_cmp_SavReader(self):
        """Comparing objects of class SavReader"""
        self.assertTrue(self.data == self.data)
        self.assertFalse(self.data > self.data)
        self.assertFalse(self.data < self.data)

    @unittest.skipIf(sys.version_info[0] > 2, "cmp not available in Python3")
    def test_cmp(self):
        self.assertEquals(cmp(self.data, 0), 1)
        self.assertEquals(cmp(self.data, 1), 0)
        self.assertEquals(cmp(self.data, 2), -1)
        self.assertEquals(cmp(self.data, self.data), 0) 

    def tearDown(self):
        self.data.close()

if __name__ == "__main__":
    unittest.main()
