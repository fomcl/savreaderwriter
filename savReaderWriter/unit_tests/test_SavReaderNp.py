#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import datetime
import tempfile
import os

try:
    import numpy as np
    import numpy.testing
    numpyOK = True
except ImportError:
    numpyOK = False

from savReaderWriter import *
from savReaderNp import *
from py3k import *

def try_remove(f):
    try:
        os.remove(f)
    except:
        pass

@unittest.skipUnless(numpyOK and isCPython, "Requires numpy, not numpypy")
class Test_SavReaderNp(unittest.TestCase):

    def setUp(self):
        self.filename = "test_data/Employee data.sav"
        self.nfilename = "test_data/all_numeric.sav"
        self.uncompressedfn = "test_data/all_numeric_uncompressed.sav"
        self.uncompresseddt = ("test_data/all_numeric_datetime_" + 
                               "uncompressed.sav")
    def test_getitem_indexing(self):
        self.npreader = SavReaderNp(self.filename)
        actual = self.npreader[0].tolist()
        desired = [(1.0, b'm', datetime.datetime(1952, 2, 3, 0, 0), 15.0, 
                    3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0)]
        self.assertEqual(actual, desired)

    def test_getitem_indexing_IndexError(self):
        self.npreader = SavReaderNp(self.filename)
        with self.assertRaises(IndexError):
            self.npreader[474]

    def test_getitem_indexing_raw(self):
        self.npreader = SavReaderNp(self.filename, rawMode=True)
        actual = self.npreader[0].tolist()
        desired = [(1.0, b'm       ', 11654150400.0, 15.0, 
                    3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0)]
        self.assertEqual(actual, desired)

    def test_getitem_slicing(self):
        self.npreader = SavReaderNp(self.filename)
        actual = self.npreader[0:2].tolist()
        desired = \
        [(1.0, b'm', datetime.datetime(1952, 2, 3, 0, 0), 15.0, 
          3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0), 
         (2.0, b'm', datetime.datetime(1958, 5, 23, 0, 0), 16.0, 
          1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0)]
        self.assertEqual(actual, desired)

    def test_getitem_indexing_IndexError(self):
        self.npreader = SavReaderNp(self.filename)
        self.assertEqual(self.npreader[475:666].tolist(), []) 

    def test_getitem_striding(self):
        self.npreader = SavReaderNp(self.filename)
        actual = self.npreader[3::-1].tolist()
        desired = \
        [(4.0, b'f', datetime.datetime(1947, 4, 15, 0, 0), 8.0, 
          1.0, 21900.0, 13200.0, 98.0, 190.0, 0.0), 
         (3.0, b'f', datetime.datetime(1929, 7, 26, 0, 0), 12.0, 
          1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0), 
         (2.0, b'm', datetime.datetime(1958, 5, 23, 0, 0), 16.0, 
          1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0), 
         (1.0, b'm', datetime.datetime(1952, 2, 3, 0, 0), 15.0, 
          3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0)]
        self.assertEqual(actual, desired)

    # ---------------

    def test_to_structured_array_inmemory(self):
        self.npreader = SavReaderNp(self.filename)
        actual = self.npreader.to_structured_array()[:3]

        obj = \
        {'formats': ['<f4', 'S1', '<M8[us]', '<f4', '<f2',
                     '<f8', '<f8', '<f4', '<f8', '<f2'],
         'names': [u'id', u'gender', u'bdate', u'educ', u'jobcat',
                   u'salary', u'salbegin', u'jobtime', u'prevexp', 
                   u'minority'],
         'titles': [u'Employee Code', u'Gender', u'Date of Birth',
                    u'Educational Level (years)', u'Employment Category',
                    u'Current Salary', u'Beginning Salary', 
                    u'Months since Hire', u'Previous Experience (months)',
                    u'Minority Classification']}
        desired = np.array(\
        [(1.0, b'm', datetime.datetime(1952, 2, 3, 0, 0), 15.0, 
          3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0),
         (2.0, b'm', datetime.datetime(1958, 5, 23, 0, 0), 16.0, 
          1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0),
         (3.0, b'f', datetime.datetime(1929, 7, 26, 0, 0), 12.0, 
          1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0)],
        dtype=np.dtype(obj))
        #numpy.testing.assert_allclose(actual, desired, rtol=1e-5)
        self.assertEqual(actual.tolist(), desired.tolist())
        self.assertEqual(actual.dtype, desired.dtype)
        self.assertEqual(actual.dtype.fields["salary"][2], u"Current Salary")

    def test_to_structured_array_inmemory_raw(self):
        self.npreader = SavReaderNp(self.filename, rawMode=True)
        actual = self.npreader.to_structured_array()[:3].tolist()
        desired = \
        [(1.0, b'm', 11654150400.0, 15.0, 3.0,
          57000.0, 27000.0, 98.0, 144.0, 0.0),
         (2.0, b'm', 11852956800.0, 16.0, 1.0, 
          40200.0, 18750.0, 98.0, 36.0, 0.0),
         (3.0, b'f', 10943337600.0, 12.0, 1.0, 
          21450.0, 12000.0, 98.0, 381.0, 0.0)]
        self.assertEqual(actual, desired)
  
    def test_to_structured_array_memmap(self):
        self.npreader = SavReaderNp(self.filename)
        mmapfile = tempfile.mkstemp()[1]
        actual = self.npreader.to_structured_array(mmapfile)[:3].tolist()
        desired = \
        [(1.0, b'm', datetime.datetime(1952, 2, 3, 0, 0), 15.0, 
          3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0),
         (2.0, b'm', datetime.datetime(1958, 5, 23, 0, 0), 16.0, 
          1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0),
         (3.0, b'f', datetime.datetime(1929, 7, 26, 0, 0), 12.0, 
          1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0)]
        self.assertEqual(actual, desired)
        try_remove(mmapfile)

    def test_to_structured_array_memmap_raw(self):
        self.npreader = SavReaderNp(self.filename, rawMode=True)
        mmapfile = tempfile.mkstemp()[1]
        actual = self.npreader.to_structured_array(mmapfile)[:3].tolist()
        desired = \
        [(1.0, b'm', 11654150400.0, 15.0, 3.0,
          57000.0, 27000.0, 98.0, 144.0, 0.0),
         (2.0, b'm', 11852956800.0, 16.0, 1.0, 
          40200.0, 18750.0, 98.0, 36.0, 0.0),
         (3.0, b'f', 10943337600.0, 12.0, 1.0, 
          21450.0, 12000.0, 98.0, 381.0, 0.0)]
        self.assertEqual(actual, desired)
        try_remove(mmapfile)

    def test_getitem_then_iter(self):
        """check if cursor is rewound after __getitem__"""
        self.npreader = SavReaderNp(self.filename)
        self.npreader[5]
        actual = next(iter(self.npreader))
        desired = \
        (1.0, b'm', datetime.datetime(1952, 2, 3, 0, 0), 15.0, 
         3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0)
        self.assertEqual(actual, desired)

    def test_to_ndarray(self):
        self.npreader = SavReaderNp(self.nfilename)
        actual = self.npreader.to_ndarray()[:5, :]
        records = [[0.0, np.nan], [1.0, 1.0], [2.0, 4.0], 
                   [3.0, 9.0], [4.0, 16.0]]
        desired = np.array(records)
        numpy.testing.assert_array_equal(actual, desired)

    def test_uncompressed_to_ndarray(self):
        self.npreader = SavReaderNp(self.uncompressedfn)
        actual = self.npreader.to_ndarray()[:5, :]
        records = [[0.0, np.nan], [1.0, 1.0], [2.0, 4.0], 
                   [3.0, 9.0], [4.0, 16.0]]
        desired = np.array(records)
        numpy.testing.assert_array_equal(actual, desired)

    def test_uncompressed_to_structured_array(self):
        self.npreader = SavReaderNp(self.uncompressedfn)
        actual = self.npreader.to_structured_array()[:5]
        records = [[0.0, np.nan], [1.0, 1.0], [2.0, 4.0], 
                   [3.0, 9.0], [4.0, 16.0]]
        desired = np.array(records)
        desired.shape = (10,)
        obj = dict(names=[u'v1', u'v2'], 
                   formats=[u'<f8', u'<f8'],
                   titles=[u'col_000', u'col_001'])
        desired.dtype = np.dtype(obj)
        self.assertEqual(actual.shape, desired.shape)
        self.assertEqual(actual.dtype, desired.dtype)
        numpy.testing.assert_array_equal(actual.tolist(), desired.tolist())

    def test_uncompressed_dt_to_ndarray(self):
        self.npreader = SavReaderNp(self.uncompresseddt)
        self.assertRaises(ValueError,  self.npreader.to_ndarray, ())

    def test_uncompressed_dt_to_ndarray_raw(self):
        self.npreader = SavReaderNp(self.uncompresseddt, rawMode=True)
        actual = self.npreader.to_ndarray()[:2]
        actual[:] = np.where(actual < 10 ** -200, np.nan, actual).tolist()
        desired = [[np.nan, np.nan], [1, 11654150400]]
        numpy.testing.assert_array_equal(actual, desired)

    def test_uncompressed_dt_to_structured_array(self):
        self.npreader = SavReaderNp(self.uncompresseddt)
        actual = self.npreader.to_structured_array()[:2].tolist()
        desired = [(0.0, datetime.datetime(1, 1, 1, 0, 0)),
                   (1.0, datetime.datetime(1952, 2, 3, 0, 0))]
        numpy.testing.assert_array_equal(actual, desired)

    def test_uncompressed_dt_to_structured_array_raw(self):
        self.npreader = SavReaderNp(self.uncompresseddt, rawMode=True)
        actual = self.npreader.to_structured_array()[:2]
        actual["v2"][0] = np.nan if actual["v2"][0] < 10 ** -200 \
                          else actual["v2"][0]
        desired = [(0.0, np.nan), (1.0, 11654150400)]
        numpy.testing.assert_array_equal(actual.tolist(), desired)

    def test_ioUtf8_structured_array(self):
        self.npreader = SavReaderNp("test_data/greetings.sav", ioUtf8=True)
        actual = self.npreader.to_structured_array()[u"greeting"].tolist()
        actual = [item.rstrip() for item in actual]  # oddity in the test data
        actual = actual[1:-1]
        desired = \
        [(b'\xe0\xa6\xa8\xe0\xa6\xae\xe0\xa6\xb8\xe0\xa7\x8d'
          b'\xe0\xa6\x95\xe0\xa6\xbe\xe0\xa7\xb0'),
         (b'\xe0\xa6\x86\xe0\xa6\xb8\xe0\xa6\xb8\xe0\xa6\xbe'
          b'\xe0\xa6\xb2\xe0\xa6\xbe\xe0\xa6\xae\xe0\xa7\x81'
          b'\xe0\xa6\x86\xe0\xa6\xb2\xe0\xa6\xbe\xe0\xa6\x87'
          b'\xe0\xa6\x95\xe0\xa7\x81\xe0\xa6\xae'),
         b'Greetings and salutations',
         (b'\xe1\x83\x92\xe1\x83\x90\xe1\x83\x9b\xe1\x83\x90\xe1' 
          b'\x83\xa0\xe1\x83\xaf\xe1\x83\x9d\xe1\x83\x91\xe1\x83\x90'),
         (b'\xd0\xa1\xd3\x99\xd0\xbb\xd0\xb5\xd0\xbc\xd0\xb5\xd1'
          b'\x82\xd1\x81\xd1\x96\xd0\xb7 \xd0\xb1\xd0\xb5'),
         (b'\xd0\x97\xd0\xb4\xd1\x80\xd0\xb0\xd0\xb2\xd1\x81'
          b'\xd1\x82\xd0\xb2\xd1\x83\xd0\xb9\xd1\x82\xd0\xb5'),
         b'\xc2\xa1Hola!',
         b'Gr\xc3\xbcezi',
         (b'\xe0\xb8\xaa\xe0\xb8\xa7\xe0\xb8\xb1\xe0\xb8\xaa'
         b'\xe0\xb8\x94\xe0\xb8\xb5'),
         b'Bondjo\xc3\xbb']
        self.assertEqual(actual, desired)
      
    def tearDown(self):
        self.npreader.close()

if __name__ == "__main__":
    unittest.main()

