#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
from pprint import pprint as print
import os
import re
import datetime
from math import ceil
from ctypes import *
from functools import wraps
from itertools import chain
from bisect import bisect

import numpy as np

import sys; sys.path.insert(0, "/home/antonia/Desktop/savreaderwriter")
from savReaderWriter import *
from error import *
from helpers import *

# TODO: now focuses entirely on structured arrays (heterogeneous), also for ndarrays (homogeneous)

try:
    xrange
except NameError:
    xrange = range

try:
   from itertools import izip
except ImportError:
   izip = zip

class SavReaderNp(SavReader):

    """
    Read SPSS .sav file data into a numpy array (either in-memory or mmap)

    Typical use:
    from contextlib import closing
    with closing(SavReaderNp("Employee data.sav")) as reader_np: 
        array = reader_np.toarray("/tmp/test.dat") # memmapped array 
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
        self.unpack = self.getStruct(self.varTypes, self.varNames).unpack_from 
        self.init_funcs()
        self.gregorianEpoch = datetime.datetime(1582, 10, 14, 0, 0, 0)
        self.do_convert_datetimes = True
        self.nrows, self.ncols = self.shape

    def _items(self, start, stop, step):
        """Helper function for __getitem__"""
        for case in xrange(start, stop, step):
            self.seekNextCase(self.fh, case)
            self.wholeCaseIn(self.fh, byref(self.caseBuffer))
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
            yield record

    def convert_datetimes(func):
        """Decorator to convert all the SPSS datetimes into datetime.datetime
        values. Missing datetimes are converted into the value 
        datetime.datetime(1, 1, 1, 0, 0)"""
        def _convert_datetimes(self, *args):
            #print("@convert_datetimes called by: %s" % func.__name__)
            array = func(self, *args)
            if (self.rawMode or not self.datetimevars or not \
                self.do_convert_datetimes):
                return array

            # calculate count so fromiter can pre-allocate
            count = self.nrows if not args else -1
            if len(args) == 1 and isinstance(args[0], slice):
                start, stop, step = args[0].indices(self.nrows)
                count = (stop - start) // step

            # now fill the array with datetimes
            dt_array = array.astype(self.datetime_dtype)            
            for varName in self.uvarNames:
                if not varName in self.datetimevars:
                    continue
                datetimes = (self.spss2numpyDate(dt) for dt in array[varName])
                dt_array[varName] = np.fromiter(datetimes, "datetime64[us]", count)
            return dt_array
        return _convert_datetimes

    @convert_datetimes
    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y], where y may be int or slice"""
        is_slice = isinstance(key, slice)
        is_index = isinstance(key, int)
        
        if is_slice:
            start, stop, step = key.indices(self.nrows)
            records = (item for item in self._items(start, stop, step))
            count = (stop - start) // step
            record = np.fromiter(iter(records), self.struct_dtype, count)
        elif is_index:
            if abs(key) > self.nrows - 1:
                raise IndexError("index out of bounds")
            key = self.nrows + key if key < 0 else key
            self.seekNextCase(self.fh, key)
            self.wholeCaseIn(self.fh, self.caseBuffer)
            record = np.fromstring(self.caseBuffer, self.struct_dtype)
        else:
            raise TypeError("slice or int required")

        # rewind for possible subsequent call to __iter__
        self.seekNextCase(self.fh, 0)
        return record

    def __iter__(self):
        """x.__iter__() <==> iter(x). Yields records as a tuple.
        If rawMode=True, trailing spaces of strings are not removed
        and SPSS dates are not converted into datetime dates"""
        varNames = self.uvarNames
        varTypes = self.uvarTypes
        datetimevars = self.datetimevars
        shortcut = self.rawMode or not self.do_convert_datetimes or \
                   not datetimevars
        for row in xrange(self.nrows):
            self.wholeCaseIn(self.fh, self.caseBuffer)
            record = self.unpack(self.caseBuffer)
            if shortcut:
                yield record
                continue
            # TODO: consider: http://docs.scipy.org/doc/numpy/reference/generated/numpy.core.defchararray.rstrip.html#numpy.core.defchararray.rstrip
            yield tuple([self.spss2numpyDate(value) if v in datetimevars else
                         value.rstrip() if varTypes[v] else value for value, v
                         in izip(record, varNames)])
      
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
        """Returns a dictionary of variable names, as unicode strings (keys)
        and variable types (values, int)"""
        return {v.decode(self.fileEncoding): t for 
                v, t in self.varTypes.items()}

    @memoized_property
    def uformats(self):
        """Returns a dictionary of variable names (keys) and SPSS formats 
        (values), both as unicode strings"""
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
    def is_homogeneous(self):
        """Returns boolean that indicates whether the dataset contains only 
        numerical variables (datetimes excluded)"""
        return not max(list(self.varTypes.values())) and not self.datetimevars

    @memoized_property
    def struct_dtype(self):
        """Get the struct dtype of the binary record"""
        if self.is_homogeneous:
            byteorder = u"<" if self.byteorder == u"little" else u">"
            return np.dtype(byteorder + u"d")
        fmt8 = lambda varType: int(ceil(varType / 8.) * 8)
        varTypes = [self.varTypes[varName] for varName in self.varNames]
        byteorder = u"<" if self.byteorder == "little" else u">"
        formats = [u"a%d" % fmt8(t) if t else u"%sd" % 
                   byteorder for t in varTypes]
        obj = dict(names=self.uvarNames, formats=formats, titles=self.titles)
        return np.dtype(obj)

    @memoized_property
    def trunc_dtype(self):
        """Derive the numpy dtype from the SPSS _display_ formats.

        The following conversions are made:
        ---------+--------
        spss     | numpy
        ---------+--------
        <= F2    | float16
        F3-F5    | float32
        >= F5    | float64
        datetime | float64
        A1 >=    | S1 >=
        Note that all numerical values are stored in SPSS files as double
        precision floats. The SPSS display formats are used to create a more
        compact dtype. Datetime formats are never shrunk to a more compact 
        format. In the table above, only F and A formats are displayed, but
        other numerical (e.g. DOLLAR) or string (AHEX) are treated the same
        way, e.g. DOLLAR5.2 will become float64.
        """
        if self.is_homogeneous and self.rawMode:
            return self.struct_dtype
        dst_fmts = ["f2", "f5", "f8", "f8"]
        get_dtype = lambda src_fmt: dst_fmts[bisect([2, 5, 8], src_fmt)]
        widths = [int(re.search(u"\d+", self.uformats[v]).group(0)) 
                  for v in self.uvarNames]
        formats = [u'a%s' % widths[i] if self.uvarTypes[v] else u"f8" if 
                   v in self.datetimevars else get_dtype(widths[i]) for 
                   i, v in enumerate(self.uvarNames)]
        obj = dict(names=self.uvarNames, formats=formats, titles=self.titles)
        return np.dtype(obj)

    @memoized_property
    def datetime_dtype(self):
        """Return the modified dtype in order to accomodate datetime.datetime
        values that were originally datetimes, stored as floats, in the SPSS
        file"""
        if not self.datetimevars:
            return self.trunc_dtype
        formats = ["datetime64[us]" if name in self.datetimevars else 
                   fmt for (title, name), fmt in self.trunc_dtype.descr]
        obj = dict(names=self.uvarNames, formats=formats, titles=self.titles)
        return np.dtype(obj)

    @memoize
    def spss2numpyDate(self, spssDateValue):
        """Convert an SPSS date into a numpy datetime64 date. Errors are
        returned as datetime.datetime(datetime.MINYEAR, 1, 1, 0, 0, 0)"""
        try:
            theDate = self.gregorianEpoch + datetime.timedelta(seconds=spssDateValue)
            #theDate = np.datetime64(theDate)
            return theDate
        except (OverflowError, TypeError, ValueError):
            return datetime.datetime(datetime.MINYEAR, 1, 1, 0, 0, 0)

    @convert_datetimes
    def toarray2(self):
        # slower than toarray!
        from numpy.ctypeslib import ndpointer

        dtype = [(name.encode(self.fileEncoding), fmt) for 
                 (title, name), fmt in self.struct_dtype.descr]
        self.wholeCaseIn.argtypes = [c_int, ndpointer(dtype)]

        array = np.empty(self.nrows, dtype)
        for row in xrange(self.nrows):
            self.wholeCaseIn(self.fh, array[row:row + 1])

        self.wholeCaseIn.argtypes = [c_int, POINTER(c_char * self.record_size)]
        return array

    def convert_missings(func):
        """Decorator to recode numerical missing values, unless they are 
        datetimes"""
        @wraps
        def _convert_missings(*args):
            if self.rawMode:
                return array
            cutoff = 10e-200
            sysmis = self.recodeSysmisTo
            for v in self.uvarNames:
                if v in self.datetimevars or self.uvarTypes[v]:
                    continue
                array[v] = np.where(array[v] < cutoff, sysmis, array[v])
                if hasattr(array, "flush"):  # memmapped
                    array.flush()
            return array
        return func

    @convert_datetimes
    @convert_missings
    def toarray(self, filename=None):
        """Return the data in <savFileName> as a structured array, optionally
        using <filename> as a memmapped file."""
        self.do_convert_datetimes = False  # no date conversion in __iter__ 
        if filename:
            array = np.memmap(filename, self.trunc_dtype, 'w+', shape=self.nrows)
            for row, record in enumerate(self):
                array[row] = record
            #array.flush()
        else:
            array = np.fromiter(self, self.trunc_dtype, self.nrows)
        self.do_convert_datetimes = True
        return array

    def to_ndarray(self):
        values = chain.from_iterable(self)
        dtype = np.dtype("float64") 
        count = np.prod(self.shape) 
        array = np.fromiter(values, dtype, count)
        array.shape = self.shape 
        return array 

    def all(self, filename=None):
        """Wrapper for toarray; overrides the SavReader version"""
        return self.toarray(filename)


if __name__ == "__main__":
    import time
    from contextlib import closing
    savFileName = "./test_data/all_numeric.sav"
    kwargs = dict( \
    savFileName = savFileName,
    varNames = ["v1", "v2"],
    varTyoes = {"v1": 0, "v2": 0} )
    if not os.path.exists(savFileName):
        with SavWriter(**kwargs) as writer:
            for i in xrange(10 ** 6):
                writer.writerow([i, 666])

    klass = globals()[sys.argv[1]]
    start = time.time() 
    filename = "./test_data/Employee data.sav"
    filename = "./test_data/greetings.sav"
    filename = "./test_data/all_numeric.sav"
    #filename = '/home/antonia/Desktop/big.sav'
    #filename = '/home/albertjan/nfs/Public/bigger.sav'
    with closing(klass(filename, rawMode=False, ioUtf8=False)) as sav:
        #print(sav.struct_dtype.descr)
        #array = sav.tondarray()
        array = sav.toarray() 
        print(sav.formats)
        #sav.all()
        #for record in sav:
            #print(record)
            #pass  
    print("%s version: %5.3f" % (sys.argv[1], (time.time() - start)))


