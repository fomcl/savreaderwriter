#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
import ctypes
import savReaderWriter as rw

# see: http://stackoverflow.com/questions/26895002/python-module-savreaderwriter-causing-segmentation-fault
class test_SavWriter_throws_no_segfault(unittest.TestCase):

    def setUp(self):
        self.savFileName = os.path.join(tempfile.gettempdir(), "somefile.sav")
        varNames = [b"a_string", b"a_numeric"]
        varTypes = {b"a_string": 1, b"a_numeric": 0}
        self.records = [[b"x", 1], [b"y", 777], [b"z", 10 ** 6]]
        self.args = (self.savFileName, varNames, varTypes)

    def test_check_segfault_numeric(self):        
        """Test if incorrect specification raises ctypes.ArgumentError, 
        not segfault"""
        valueLabels = {b"a_numeric": {b"1": b"male", b"2": b"female"}}
        with self.assertRaises(ctypes.ArgumentError):
            with rw.SavWriter(*self.args, valueLabels=valueLabels) as writer:
                writer.writerows(self.records)

    def test_check_segfault_char(self):        
        """Test if incorrect specification raises ctypes.ArgumentError, 
        not segfault"""
        # c_char_p is wrapped in c_char_p3k in py3k.py, hence a separate test
        valueLabels = {b"a_string": {1: b"male", 2: b"female"}}
        with self.assertRaises(ctypes.ArgumentError):
            with rw.SavWriter(*self.args, valueLabels=valueLabels) as writer:
                writer.writerows(self.records)

    def tearDown(self):
        try:
            os.remove(self.savFileName)
        except:
            pass  
    

if __name__ == "__main__":
    unittest.main()
