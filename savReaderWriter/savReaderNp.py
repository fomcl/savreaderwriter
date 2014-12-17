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
from savReaderWriter import *
from error import *
from helpers import *


# http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html
# http://docs.scipy.org/doc/numpy/reference/generated/numpy.memmap.html
# http://docs.scipy.org/doc/numpy/reference/arrays.datetime.html
# http://stackoverflow.com/questions/16601819/change-dtype-of-recarray-column-for-object-type

try:
    xrange
except NameError:
    xrange = range

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
        self.iter_converts_datetimes = True

    def _items(self, start, stop, step):
        """Helper function for __getitem__"""
        for case in xrange(start, stop, step):
            self.seekNextCase(self.fh, case)
            self.wholeCaseIn(self.fh, byref(self.caseBuffer))
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
            yield record.astype(self.trunc_dtype)

    def convert_datetimes(func):
        """Decorator to convert all the SPSS datetimes into datetime.datetime
        values. Missing datetimes are converted into the value 
        datetime.datetime(1, 1, 1, 0, 0)"""
        def _convert_datetimes(self, *args):
            #print("@convert_datetimes called by: %s" % func.__name__)
            array = func(self, *args)
            if self.rawMode or not self.datetimevars:
                return array

            converter = partial(self.spss2numpyDate,
                                recodeSysmisTo=date(MINYEAR, 1, 1))
            for varName in self.uvarNames:
                if not varName in self.datetimevars:
                    continue
                datetimes = (converter(dt) for dt in array[varName])
                array = array.astype(self.datetime_dtype)
                array[varName] = np.fromiter(datetimes, dtype=np.datetime64)  # TODO: this won't work in Python 3
            return array
        return _convert_datetimes

    @convert_datetimes
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
        """x.__iter__() <==> iter(x). Yields records with an astyped 
        ('truncated') dtype: single-precision floats, trailing blanks
        removed"""
        converter = partial(self.spss2numpyDate, 
                            recodeSysmisTo=date(MINYEAR, 1, 1))
        no_datetime_conversion = self.rawMode or not self.datetimevars or \
                                 not self.iter_converts_datetimes
        self.seekNextCase(self.fh, 0)  # rewind
        for row in xrange(self.shape.nrows):
            self.wholeCaseIn(self.fh, byref(self.caseBuffer))
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
            if no_datetime_conversion:
                self.iter_converts_datetimes = True  # if to_array toggled it
                yield record.astype(self.trunc_dtype)
                continue
            # This ensures that datetimes are converted when iter() is called
            # directly. It will be skipped if to_array is called
            # TODO: find a numpy solution for the list comp below
            items = [converter(record[v][0]) if v in self.datetimevars else
                     record[v][0] for v in self.uvarNames]
            record = record.astype(self.datetime_dtype)
            record[:] = tuple(items)
            yield record
      
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
    def uvarNames(self):
        """Returns a list of variable names, as unicode strings"""
        return [v.decode(self.fileEncoding) for v in self.varNames]

    @memoized_property
    def uvarTypes(self): 
        """Returns a dictionary of variable names, as unicode strings"""
        return {v.decode(self.fileEncoding): t for 
                v, t in self.varTypes.items()}

    @memoized_property
    def uformats(self):
        """Returns a dictionary of SPSS formats, as unicode strings"""
        encoding = self.fileEncoding
        return {v.decode(encoding): fmt.decode(encoding) for 
                v, fmt in self.formats.items()}

    @memoized_property
    def datetimevars(self):
        """Returns a list of the date/time variables in the dataset, if any"""
        return [varName for varName in self.uvarNames if 
                re.search("date|time", self.uformats[varName], re.I)]

    @memoized_property
    def titles(self):
        """Helper function that uses varLabels to get the titles for a dtype.
        If no varLabels are available, varNames are used instead"""
        titles =  [self.varLabels[v] if self.varLabels[v] else 
                   "col_%03d" % col for col, v in enumerate(self.varNames)]
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
        formats = [u'a%s' % re.search(u"\d+", self.uformats[v]).group(0) if
                   self.uvarTypes[v] else u"f8" for v in self.uvarNames]
        obj = dict(names=self.uvarNames, formats=formats, titles=self.titles)
        return np.dtype(obj)

    @memoized_property
    def datetime_dtype(self):
        """Return the modified dtype in order to accomodate datetime.datetime
        values that were originally datetimes, stored as floats, in the SPSS
        file"""
        if not self.datetimevars:
            return self.trunc_dtype
        formats = ["datetime64" if name in self.datetimevars else 
                   fmt for (title, name), fmt in self.trunc_dtype.descr]
        obj = dict(names=self.uvarNames, formats=formats, titles=self.titles)
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

    @convert_datetimes
    def to_array(self, filename=None):
        """Return the data in <savFileName> as a structured array, optionally
        using <filename> as a memmapped file"""
        self.iter_converts_datetimes = False
        if filename:
            array = np.memmap(filename, self.trunc_dtype, 
                              'w+', shape=self.shape.nrows)
            for row, record in enumerate(self):
                array[row] = record
            #array[:] = np.fromiter(self, self.trunc_dtype)  # MemoryError
            array.flush()
        else:
            array = np.empty(self.shape.nrows, self.trunc_dtype)
            for row in xrange(self.shape.nrows):
            #for row, record in enumerate(self):
                array[row] = self[row]
            #array = np.fromiter(self, self.trunc_dtype)  # Less efficient than loop??
        return array

    def all(self):
        """Wrapper for to_array; overrides the SavReader version"""
        return self.to_array()


if __name__ == "__main__":
    import time
    from contextlib import closing
    start = time.time()
    """
    with SavReaderNp("./test_data/Employee data.sav") as sav:
        for record in sav:
            #print(record)
            pass  

    #with closing(SavReaderNp('/home/albertjan/nfs/Public/bigger.sav')) as sav:
        #array = sav.to_array("/tmp/test.dat")
        #print(array[0])
        #print(sav.shape) 
    """
    start = time.time()
    klass = globals()[sys.argv[1]] 
    filename = "./test_data/Employee data.sav"
    #filename = '/home/albertjan/nfs/Public/bigger.sav'
    with closing(klass(filename)) as sav:
        array = sav.all()
        #records = sav.all() #"/tmp/test.dat")
    print("%s version: %5.3f" % (sys.argv[1], (time.time() - start)))

    """
    start = time.time()
    klass = SavReader
    filename = "./test_data/Employee data.sav"
    #filename = '/home/albertjan/nfs/Public/bigger.sav'
    with closing(klass(filename)) as sav:
        for record in sav:
            pass 
        #records = sav.all() #"/tmp/test.dat")
    print("Standard version: %5.3f" % (time.time() - start))

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
    """

