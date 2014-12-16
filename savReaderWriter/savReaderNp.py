#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
from pprint import pprint as print
import os
import re
from datetime import timedelta, datetime, date, MINYEAR
from math import ceil
from ctypes import *
from functools import wraps, partial

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

def memoized_property(fget):
    """
    Return a property attribute for new-style classes that only calls its 
    getter on the first access. The result is stored and on subsequent 
    accesses is returned, preventing the need to call the getter any more.
    source: https://pypi.python.org/pypi/memoized-property/1.0.1
    """
    attr_name = "_" + fget.__name__
    @wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)
    return property(fget_memoized)


class SavReaderNp(SavReader):

    """
    Read SPSS .sav file data into a numpy array (either in-memory or mmap)

    Typical use:
    from contextlib import closing
    with closing(SavReaderNp("Employee data.sav")) as reader_np: 
        array = reader_np.to_array("/tmp/test.dat") # memmapped array 
    """

    def __init__(self, savFileName, recodeSysmisTo=np.nan, rawMode=False, 
                 ioUtf8=False, ioLocale=None):
        super(SavReaderNp, self).__init__(savFileName, 
           ioUtf8=ioUtf8, ioLocale=ioLocale)

        self.savFileName = savFileName
        self.recodeSysmisTo = recodeSysmisTo
        self.rawMode = rawMode
        self.ioUtf8 = ioUtf8
        self.ioLocale = ioLocale

        self.caseBuffer = self.getCaseBuffer()
        self.init_funcs()
        self.gregorianEpoch = datetime(1582, 10, 14, 0, 0, 0)

    def _items(self, start, stop, step):
        for case in xrange(start, stop, step):
            self.seekNextCase(self.fh, case)
            self.wholeCaseIn(self.fh, byref(self.caseBuffer))
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
            yield record.astype(self.trunc_dtype)

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y], where y may be int or slice"""
        is_slice = isinstance(key, slice)
        is_index = isinstance(key, int)

        if is_slice:
            start, stop, step = key.indices(self.shape.nrows)
            records = (item for item in self._items(start, stop, step)) 
            return np.fromiter(records, self.trunc_dtype)

        elif is_index:
            if abs(key) > self.shape.nrows - 1:
                raise IndexError("index out of bounds")
            key = self.shape.nrows + key if key < 0 else key
            self.seekNextCase(self.fh, key)
            self.wholeCaseIn(self.fh, byref(self.caseBuffer))
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
            return record.astype(self.trunc_dtype)

        else:
            raise TypeError("slice or int required")

    def __iter__(self):
        """x.__iter__() <==> iter(x). Yields records with a 'truncated' dtype:
        single-precision floats, trailing blanks removed"""
        self.seekNextCase(self.fh, 0)  # rewind
        for row in xrange(self.shape.nrows):
            self.wholeCaseIn(self.fh, byref(self.caseBuffer))
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
            yield record.astype(self.trunc_dtype)
      
    def init_funcs(self):
        """Helper to initialize C functions of the SPSS I/O module: set their
        argtypes and errcheck attributes""" 
        self.seekNextCase = self.spssio.spssSeekNextCase
        self.seekNextCase.argtypes = [c_int, c_long]
        self.seekNextCase.errcheck = self.errcheck

        self.record_size = sizeof(self.caseBuffer)
        self.wholeCaseIn = self.spssio.spssWholeCaseIn
        self.wholeCaseIn.argtypes = [c_int, POINTER(c_char * self.record_size)]
        self.wholeCaseIn.errcheck = self.errcheck

    def errcheck(self, retcode, func, arguments):
        """Checks for return codes > 0 when calling C functions of the 
        SPSS I/O module"""
        if retcode > 0:
            error = retcodes.get(retcode, retcode)
            msg = "function %r with arguments %r throws error: %s"
            msg = msg % (func.__name__, arguments, error)
            raise SPSSIOError(msg, retcode)

    @memoized_property
    def titles(self):
        """Helper function that uses varLabels to get the titles for a dtype.
        If no varLabels are available, varNames are used instead"""
        titles =  [self.varLabels[varName] if self.varLabels[varName]
                   else varName for varName in self.varNames]
        return [title.decode(self.fileEncoding) for title in titles]

    @memoized_property
    def struct_dtype(self):
        """Get the struct dtype for the binary record"""
        fmt8 = lambda varType: int(ceil(varType / 8.) * 8)
        varTypes = [self.varTypes[varName] for varName in self.varNames]
        byteorder = u"<" if self.byteorder == "little" else u">"
        names = [v.decode(self.fileEncoding) for v in self.varNames]
        formats = [u"a%d" % fmt8(t) if t else u"%sd" % 
                   byteorder for t in varTypes]
        obj = dict(names=names, formats=formats, titles=self.titles)
        return np.dtype(obj)

    @memoized_property
    def trunc_dtype(self):
        """Get the truncated (single-precision, no trailing spaces) dtype"""
        encoding = self.fileEncoding 
        varNames = [v.decode(encoding) for v in self.varNames] 
        varTypes = {v.decode(encoding): t for v, t in self.varTypes.items()}
        formats = {v.decode(encoding): fmt.decode(encoding) for 
                                       v, fmt in self.formats.items()}
        formats = [u'a%s' % re.search(u"\d+", formats[v]).group(0) if 
                   varTypes[v] else u"f8" for v in varNames]
        obj = dict(names=varNames, formats=formats, titles=self.titles)
        return np.dtype(obj)

    @memoized_property
    def datetime_dtype(self):
        """Return the modified dtype in order to accomodate datetime.datetime
        values that were originally datetimes, stored as floats, in the SPSS
        file"""
        is_datetime = re.compile(b"date|time", re.I)
        datetimevars = [varName for varName in self.varNames if 
                        is_datetime.search(self.formats[varName])]
        if not datetimevars:
            return self.trunc_dtype
        descr = self.trunc_dtype.descr
        names = [name for (title, name), fmt in descr]
        formats = ["datetime64" if name in datetimevars else 
                   fmt for (title, name), fmt in descr]
        titles = [title for (title, name), fmt in descr]
        obj = dict(names=names, formats=formats, titles=titles)
        return np.dtype(obj)

    def spss2numpyDate(self, spssDateValue, recodeSysmisTo=np.nan, _memo={}):
        """Convert an SPSS date into a numpy datetime64 date"""
        try:
            return _memo[spssDateValue]
        except KeyError:
            pass
        try:
            theDate = self.gregorianEpoch + timedelta(seconds=spssDateValue)
            theDate = np.datetime64(theDate)
            _memo[spssDateValue] = theDate
            return theDate
        except (OverflowError, TypeError, ValueError):
            return recodeSysmisTo

    def convert_datetimes(func):
        """Decorator to convert all the SPSS datetimes into datetime.datetime
        values"""
        def _convert_datetimes(self, filename=None):
            array = func(self, filename)
            if self.rawMode:
                return array

            converter = partial(self.spss2numpyDate,
                                recodeSysmisTo=date(MINYEAR, 1, 1))
            is_datetime = re.compile(b"date|time", re.I)
            datetimevars = [varName for varName in self.varNames if 
                            is_datetime.search(self.formats[varName])]
            for varName in self.varNames:
                if not varName in datetimevars:
                    continue
                datetimes = (converter(dt) for dt in array[varName])
                array = array.astype(self.datetime_dtype)
                array[varName] = np.fromiter(datetimes, dtype=np.datetime64)
            return array
        return _convert_datetimes

    @convert_datetimes
    def to_array(self, filename=None):
        """Return the data in <savFileName> as a structured array, optionally
        using <filename> as a memmapped file"""
        if filename:
            array = np.memmap(filename, self.trunc_dtype, 
                              'w+', shape=self.shape.nrows)
            for row in xrange(self.shape.nrows):
                array[row] = self[row]
            array.flush()
        else:
            array = np.fromiter(self, self.trunc_dtype)
        return array

if __name__ == "__main__":
    import time
    start = time.time()
    sav = SavReaderNp("./test_data/Employee data.sav")
    array = sav.to_array() #"/tmp/test.dat")
    for lino, line in enumerate(sav):
        if lino == 473:
            print(line)
    sav.close()
    print("Numpy version: %3.1f" % (time.time() - start))
    sav = SavReader("./test_data/Employee data.sav")
    for lino, line in enumerate(sav):
        if lino == 473:
            print(line)
    sav.close()
    print("Standard version: %3.1f" % (time.time() - start))
    xxx 
    print(array[:5])  
    print(sav[::-5])
    print(sav[0])
    array = sav.to_array()
    print(array[:5]) 
    print("*****************************")
    array = sav.to_array("/tmp/test.dat")
    print(array['id'])
    print(array.shape) 
    
    df = pd.DataFrame(array) #, dtype=np.dtype("f4"))
    df.bdate = df["bdate"].apply(sav.spss2numpyDate)
    print(df.head())

