#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import savReaderWriter as rw
from py3k import isPy3k, isCPython

class Test_spss2strDate(unittest.TestCase):

    def setUp(self):
        self.savFileName = 'test_data/test_dates.sav'
        self.reader = rw.SavReader(self.savFileName)
        self.convert = self.reader.spss2strDate

    def test_time(self): 
        got = self.convert(1, "%H:%M:%S", None)
        self.assertEqual(b'00:00:01', got)

        got = self.convert(86399, "%H:%M:%S", None)
        self.assertEqual(b'23:59:59', got)

    def test_datetime(self):
        got = self.convert(11654150400.0, "%Y-%m-%d %H:%M:%S", None)
        self.assertEqual(b'1952-02-03 00:00:00', got)

        got = self.convert(11654150400.0, "%Y-%m-%d", None)
        self.assertEqual(b'1952-02-03', got)

        got = self.convert(11654150400.0, "%d-%m-%Y", None)
        self.assertEqual(b'03-02-1952', got)

    msg = "requires mx package (no Python 3 or Pypy)"
    @unittest.skipIf(isPy3k or not isCPython, msg)
    def test_datetime_pre1900(self):
        got = self.convert(0.0, "%Y-%m-%d %H:%M:%S", None)
        self.assertEqual(b'1582-10-14 00:00:00', got)

    def test_dtime(self):
        got = self.convert(256215.0, "%d %H:%M:%S", None)
        self.assertEqual(b'02 23:10:15', got)

        got = self.convert(13508553600, "%d %H:%M:%S", None)
        self.assertEqual(b'156349 00:00:00', got)

    def test_invalid_datetime(self):
        got = self.convert(b"invalid", "%Y-%m-%d %H:%M:%S", None)
        self.assertEqual(None, got)

        got = self.convert(b"invalid", "%Y-%m-%d %H:%M:%S", b"<invalid>")
        self.assertEqual(b"<invalid>", got)

    def tearDown(self):
        self.reader.close()

if __name__ == "__main__":
    unittest.main()
