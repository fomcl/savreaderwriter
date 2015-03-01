#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import closing
import unittest
import savReaderWriter as rw

# N format = numerical with leading zeroes
class Test_N_Format(unittest.TestCase):

    def setUp(self):
        self.savFileName = "test_data/leading_zero.sav"

    def test_n_format(self):
        with closing(rw.SavReader(self.savFileName)) as reader:
            records_got = reader.all()
        records_expected = [[b'0000000001'], [b'0000000002']]
        self.assertEqual(records_expected, records_got)

    def test_n_format_ioUtf8(self):
        with closing(rw.SavReader(self.savFileName, ioUtf8=True)) as reader:
            records_got = reader.all()
        records_expected = [[u'0000000001'], [u'0000000002']]
        self.assertEqual(records_expected, records_got)

if __name__ == "__main__":
    unittest.main()
