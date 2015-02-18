#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import tempfile
import unittest
from pprint import pprint
import savReaderWriter as sav

"""
Metadata roundtrip in unicode mode, see issue #32

Previously **metadata in unicode mode could not be 
consumed by SavWriter as they were ustrings. 
ioUtf8=UNICODE_BMODE can be used when unicode mode
should return byte strings.
"""

# Demonstrates use of ioUtf8=UNICODE_BMODE, or ioUtf8=2. 
# This is regular unicode mode (ioUtf8=UNICODE_BMODE, or ioUtf8=1, 
# or ioUtf8=True), but data will be returned as bytes.
# TODO strings are tripled when ioLocale is specified!!! 
# Why??? It's as if this makes the I/O lib switch to codepage mode!?!
in_savFileName = "../savReaderWriter/test_data/metadata_copy_test.sav"
ioLocale = "german" if sys.platform.startswith("win") else "de_DE.cp1252"
settings = dict(ioUtf8=sav.UNICODE_BMODE) #, ioLocale=ioLocale)

# read SPSS file data
data = sav.SavReader(in_savFileName, rawMode=True, **settings)
with data:
    in_records = data.all()

# read SPSS file metadata
with sav.SavHeaderReader(in_savFileName, **settings) as header:
    metadata = header.dataDictionary()
    #pprint(metadata)

# write (unmodified) data to SPSS file
out_savFileName = os.path.join(tempfile.gettempdir(), 'out.sav')
metadata.update(settings)
with sav.SavWriter(out_savFileName, **metadata) as writer:
    writer.writerows(in_records)

# Now test whether input and output are the same
class Test_MetadataRoundTrip(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_data_same(self):
        data = sav.SavReader(out_savFileName, rawMode=True, **settings)
        with data:
            out_records = data.all()
        self.assertEqual(in_records, out_records)

    def test_metadata_same(self):
        settings = dict(ioUtf8=True, ioLocale=ioLocale)
        with sav.SavHeaderReader(in_savFileName, **settings) as header:
            in_metadata = header.dataDictionary()
        with sav.SavHeaderReader(out_savFileName, **settings) as header:
            out_metadata = header.dataDictionary()
        self.assertEqual(in_metadata, out_metadata)  

if __name__ == "__main__":
    unittest.main()


