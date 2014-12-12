#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
from pprint import pprint as print
import os
import collections
import re
import datetime
from math import ceil
from ctypes import *
import numpy as np

import savReaderWriter as rw
from error import *


# http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html
# http://docs.scipy.org/doc/numpy/reference/generated/numpy.memmap.html
# http://docs.scipy.org/doc/numpy/reference/arrays.datetime.html
# http://stackoverflow.com/questions/16601819/change-dtype-of-recarray-column-for-object-type

class SavReaderNp(rw.Header):

    """
    Read SPSS .sav file data into a numpy array (either in-memory or mmap)
    """

    def __init__(self, savFileName, ioUtf8=False, ioLocale=None):
        super(SavReaderNp, self).__init__(savFileName, mode="rb", 
          refSavFileName=None, ioUtf8=ioUtf8, ioLocale=ioLocale)
        self.savFileName = savFileName
        self.caseBuffer = self.getCaseBuffer()
        #self.unpack = self.getStruct(self.varTypes, self.varNames).unpack_from
        self.init_funcs()
        self.gregorianEpoch = datetime.datetime(1582, 10, 14, 0, 0, 0)

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
            msg = "function %r with arguments %r throws error: %s" % error
            raise SPSSIOError(msg, retcode)

    @property
    def titles(self):
        return [self.varLabels[varName] if self.varLabels[varName] else 
                "title %02d" % i for i, varName in enumerate(self.varNames)]

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

    @property
    def shape(self):
        Shape = collections.namedtuple("Shape", "nrows ncols")
        return Shape(self.numberofCases, self.numberofVariables)
 
    def to_array(self, filename=None):
        if not filename:
            #array = np.empty(self.shape, np.object) # self.trunc_dtype)
            array = np.empty(self.shape, self.trunc_dtype)
            for row, record in enumerate(self):
                array[row, :] = record
            return array
            #return np.fromiter(self, self.trunc_dtype)
        else:
            #array = np.memmap(filename, np.object, 'w+', shape=self.shape)
            array = np.memmap(filename, self.trunc_dtype, 'w+', shape=self.shape)  
            for row, record in enumerate(self):
                #array[row] = self.unpack(self.caseBuffer)
                array[row, :] = record
            array.flush()
            return array #array.astype(self.trunc_dtype)

    def spss2numpyDate(self, spssDateValue, fmt, recodeSysmisTo=np.nan, _memoize={}):
        try:
            return _memoize[spssDateValue]
        except KeyError:
            pass
        try:
            theDate = self.gregorianEpoch + datetime.timedelta(seconds=spssDateValue)
            return np.datetime64(theDate)
        except (OverflowError, TypeError, ValueError):
            return recodeSysmisTo

if __name__ == "__main__":
    sav = SavReaderNp("./test_data/Employee data.sav")
    #for record in sav:
    #    print(record)
    #array = sav.to_array() 
    #print(array.shape) 
    #print(array)
    print("*****************************")
    filename = "/tmp/test.dat"
    array = sav.to_array(filename)
    print(array.shape) 
    print(array[0, :])
    print(sav.shape)
    


