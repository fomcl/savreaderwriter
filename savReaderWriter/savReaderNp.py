#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
#from pprint import pprint as print
import os
import re
from datetime import timedelta, datetime
from math import ceil
from ctypes import *

import numpy as np
import pandas as pd

import sys; sys.path.insert(0, "/home/antonia/Desktop/savreaderwriter")
import savReaderWriter as rw
from error import *


# http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html
# http://docs.scipy.org/doc/numpy/reference/generated/numpy.memmap.html
# http://docs.scipy.org/doc/numpy/reference/arrays.datetime.html
# http://stackoverflow.com/questions/16601819/change-dtype-of-recarray-column-for-object-type

try:
    xrange
except NameError:
    xrange = range

class SavReaderNp(rw.SavReader):

    """
    Read SPSS .sav file data into a numpy array (either in-memory or mmap)
    """

    def __init__(self, savFileName, ioUtf8=False, ioLocale=None):
        super(SavReaderNp, self).__init__(savFileName, 
           ioUtf8=ioUtf8, ioLocale=ioLocale)
        self.savFileName = savFileName
        self.caseBuffer = self.getCaseBuffer()
        #self.unpack = self.getStruct(self.varTypes, self.varNames).unpack_from
        self.init_funcs()
        self.gregorianEpoch = datetime(1582, 10, 14, 0, 0, 0)

    def __getitem__(self, key):
        """only indexing (int) is supported"""
        if abs(key) > self.shape.nrows - 1:
            raise IndexError("index out of bounds")
        key = self.shape.nrows + key if key < 0 else key
        self.seekNextCase(self.fh, key)
        self.wholeCaseIn(self.fh, byref(self.caseBuffer))
        record = np.fromstring(self.caseBuffer, self.struct_dtype)
        return record.astype(self.trunc_dtype)

    def __iter__(self):
        self.seekNextCase(self.fh, 0)  # rewind
        for row in xrange(self.shape.nrows):
            self.wholeCaseIn(self.fh, byref(self.caseBuffer))
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
            #yield self.unpack(self.caseBuffer)
            yield record.astype(self.trunc_dtype)
      
    def init_funcs(self):
        self.seekNextCase = self.spssio.spssSeekNextCase
        self.seekNextCase.argtypes = [c_int, c_long]
        self.seekNextCase.errcheck = self.errcheck

        self.record_size = sizeof(self.caseBuffer)
        self.wholeCaseIn = self.spssio.spssWholeCaseIn
        self.wholeCaseIn.argtypes = [c_int, POINTER(c_char * self.record_size)]
        self.wholeCaseIn.errcheck = self.errcheck

    def errcheck(self, retcode, func, arguments):
        if retcode > 0:
            error = retcodes.get(retcode, retcode)
            msg = "function %r with arguments %r throws error: %s"
            msg = msg % (func.__name__, arguments, error)
            raise SPSSIOError(msg, retcode)

    @property
    def titles(self):
        if hasattr(self, "titles_"):
            return self.titles_
        self.titles_ = [self.varLabels[varName] if self.varLabels[varName]
                        else varName for varName in self.varNames]
        return self.titles_

    @property
    def struct_dtype(self):
        fmt8 = lambda varType: int(ceil(varType / 8.) * 8)
        varTypes = [self.varTypes[varName] for varName in self.varNames]
        endian = "<" if self.byteorder == "little" else ">"
        formats = ['a%d' % fmt8(t) if t else '%sd' % endian for t in varTypes]
        obj = dict(names=self.varNames, formats=formats, titles=self.titles)
        return np.dtype(obj)

    @property
    def trunc_dtype(self):
        formats = ['a%s' % re.search("\d+", self.formats[v]).group(0) if 
                   self.varTypes[v] else "f4" for v in self.varNames]
        obj = dict(names=self.varNames, formats=formats, titles=self.titles)
        return np.dtype(obj)

    def to_array(self, filename=None):
        if filename:
            array = np.memmap(filename, self.trunc_dtype, 'w+', shape=self.shape.nrows)
            for row in xrange(self.shape.nrows):
                array[row] = self[row]
            array.flush()
        else:
            array = np.fromiter(self, self.trunc_dtype)
            #array = pd.DataFrame.from_records(tuple(self))
        return array

    def spss2numpyDate(self, spssDateValue, recodeSysmisTo=np.nan, _memoize={}):
        try:
            return _memoize[spssDateValue]
        except KeyError:
            pass
        try:
            theDate = self.gregorianEpoch + timedelta(seconds=spssDateValue)
            #theDate = np.datetime64(theDate)
            _memoize[spssDateValue] = theDate
            return theDate
        except (OverflowError, TypeError, ValueError):
            return recodeSysmisTo

if __name__ == "__main__":
    sav = SavReaderNp("./test_data/Employee data.sav")
    array = sav.to_array()
    print(array[:5]) 
    print("*****************************")
    array = sav.to_array("/tmp/test.dat")
    print(array.shape) 
    
    df = pd.DataFrame(array) #, dtype=np.dtype("f4"))
    df.bdate = df["bdate"].apply(sav.spss2numpyDate)
    print(df.head())
