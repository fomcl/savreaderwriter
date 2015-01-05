#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
from pprint import pprint as print
import os
import re
import datetime
import struct
from math import ceil
from ctypes import *
from functools import wraps, partial
from itertools import chain, islice
from bisect import bisect

import numpy as np

import sys; sys.path.insert(0, "/home/antonia/Desktop/savreaderwriter")
from savReaderWriter import *
from error import *
from helpers import *

# TODO:
# unittests for uncompressed .sav files
# ioLocale, ioUtf8 (latter currently fails)
# pytables integration
# numba.jit
# function to easily read mmapped array back in

from py3k import *
try:
    xrange
except NameError:
    xrange = range

try:
   from itertools import izip
except ImportError:
   izip = zip

if sys.version_info.major == 2:
   bytez = bytes
else:
   bytez = partial(bytes, encoding="utf-8")


class SavReaderNp(SavReader):

    """
    Read SPSS .sav file data into a numpy array (either in-memory or mmap)

    Typical use:
    from contextlib import closing
    with closing(SavReaderNp("Employee data.sav")) as reader_np: 
        array = reader_np.to_structured_array("/tmp/test.dat") # memmapped array 

    Note. The sav-to-array conversion is MUCH faster when uncompressed .sav 
    files are used. These are created with the SPSS command
       SAVE OUTFILE = 'some_file.sav' /UNCOMPRESSED.
    This is NOT the default in SPSS. See also SavReader documentation
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

        if self.is_uncompressed:
            self.sav = open(self.savFileName, "rb")
            self.__iter__ = self._uncompressed_iter
            self.to_ndarray = self._uncompressed_to_ndarray
            self.to_structured_array = self._uncompressed_to_structured_array  

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

    def convert_missings(func):
        """Decorator to recode numerical missing values, unless they are 
        datetimes"""
        def _convert_missings(self, *args):
            array = func(self, *args) 
            cutoff = -sys.float_info.max
            sysmis = self.recodeSysmisTo
            is_to_structured_array = func.__name__.endswith('to_structured_array')
            if self.rawMode:
                return array
            elif self.is_homogeneous and not is_to_structured_array:
                array[:] = np.where(array <= cutoff, sysmis, array)
            else:
                for v in self.uvarNames:
                    if v in self.datetimevars or self.uvarTypes[v]:
                        continue
                    array[v] = np.where(array[v] <= cutoff, sysmis, array[v])

            if hasattr(array, "flush"):  # memmapped
                array.flush()

            return array
        return _convert_missings

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
        if self.ioUtf8: return self.varNames
        return [v.decode(self.fileEncoding) for v in self.varNames]

    @memoized_property
    def uvarTypes(self): 
        """Returns a dictionary of variable names, as unicode strings (keys)
        and variable types (values, int)"""
        if self.ioUtf8: return self.varTypes
        return {v.decode(self.fileEncoding): t for 
                v, t in self.varTypes.items()}

    @memoized_property
    def uformats(self):
        """Returns a dictionary of variable names (keys) and SPSS formats 
        (values), both as unicode strings"""
        if self.ioUtf8: return self.formats
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
                   bytez("col_%03d" % col) for col, v in 
                   enumerate(self.varNames)]
        return [title.decode(self.fileEncoding) if not 
                isinstance(title, unicode) else title for title in titles]

    @memoized_property
    def is_homogeneous(self):
        """Returns boolean that indicates whether the dataset contains only 
        numerical variables (datetimes excluded). If rawMode=True, datetimes
        are also considered numeric"""
        is_all_numeric = bool( not max(list(self.varTypes.values())) )
        if self.rawMode:
            return is_all_numeric 
        return is_all_numeric and not self.datetimevars

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

        The following spss-format to numpy-dtype conversions are made:
        ---------+-------------
        spss     | numpy
        ---------+-------------
        <= F2    | float16 (f2)
        F3-F5    | float32 (f4)
        >= F5    | float64 (f8)
        datetime | float64 (f8, datetime.datetime unless rawMode)
        A1 >=    | S1 >=   (a1)
        Note that all numerical values are stored in SPSS files as double
        precision floats. The SPSS display formats are used to create a more
        compact dtype. Datetime formats are never shrunk to a more compact 
        format. In the table above, only F and A formats are displayed, but
        other numerical (e.g. DOLLAR) or string (AHEX) are treated the same
        way, e.g. DOLLAR5.2 will become float64.
        """
        #if self.is_homogeneous:
        #    return self.struct_dtype
        dst_fmts = [u"f2", u"f4", u"f8", u"f8"]
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


    # ---- functions that deal with uncompressed .sav files ----
    @memoized_property    
    def is_uncompressed(self):
        """Returns True if the .sav file was not compressed at all, False
        otherwise (i.e., neither standard, nor zlib compression was used)."""
        return self.fileCompression == b"uncompressed"

    def _uncompressed_iter(self):
        """Faster version of __iter__ that can only be used with 
        uncompressed .sav files"""
        self.sav.seek(self.offset)
        for case in xrange(self.nrows):
            yield self.unpack(self.sav.read(self.record_size))

    @property
    def offset(self):
        """Returns the position of the type 999 record, which indicates the 
        end of the metadata and the start of the case data"""
        unpack_int = lambda value: struct.unpack("i", value)
        i = 0
        while True:
            self.sav.seek(i)
            try: 
                code = unpack_int(self.sav.read(4))
            except struct.error:
                pass
            i += 1
            end_of_metadata = code == (999,)
            if end_of_metadata:
                self.sav.read(4)
                return self.sav.tell()

    @convert_datetimes
    @convert_missings
    def _uncompressed_to_structured_array(self, filename=None):
        """Read an uncompressed .sav file and return as a structured array"""
        if not self.is_uncompressed:
            raise ValueError("Only uncompressed files can be used")
        self.sav.seek(self.offset)
        if filename:
            array = np.memmap(filename, self.trunc_dtype, 'w+', shape=self.nrows)
            array[:] = np.fromfile(self.sav, self.trunc_dtype, self.nrows)
        else:
            array = np.fromfile(self.sav, self.trunc_dtype, self.nrows)
        return array

    @convert_missings
    def _uncompressed_to_ndarray(self, filename=None):
        """Read an uncompressed .sav file and return as an ndarray"""
        if not self.is_uncompressed:
            raise ValueError("Only uncompressed files can be used")
        if not self.is_homogeneous:
            raise ValueError("Need only floats and no datetimes in dataset")
        self.sav.seek(self.offset)
        count = np.prod(self.shape)
        if filename:
            array = np.memmap(filename, float, 'w+', shape=count)
            array[:] = np.fromfile(self.sav, float, count)
        else:
            array = np.fromfile(self.sav, float, count)
        return array.reshape(self.shape)
    # ------------------------------------------------------------------------ 

    @convert_datetimes
    @convert_missings
    def to_structured_array(self, filename=None):
        """Return the data in <savFileName> as a structured array, optionally
        using <filename> as a memmapped file."""
        self.do_convert_datetimes = False  # no date conversion in __iter__ 
        if filename:
            array = np.memmap(filename, self.trunc_dtype, 'w+', shape=self.nrows)
            for row, record in enumerate(self):
                array[row] = record
            #array.flush()
        else:
            if self.is_uncompressed:
                array = self._uncompressed_to_array(as_ndarray=False)
            else: 
                array = np.fromiter(self, self.trunc_dtype, self.nrows)
        self.do_convert_datetimes = True
        return array

    def all(self, filename=None):
        """Wrapper for to_structured_array; overrides the SavReader version"""
        return self.to_structured_array(filename)

    @convert_missings
    def to_ndarray(self, filename=None):
        """Converts a homogeneous, all-numeric SPSS dataset into an ndarray,
        unless the numerical variables are actually datetimes"""
        if not self.is_homogeneous:
            raise ValueError("Need only floats and no datetimes in dataset")
        elif filename:
            array = np.memmap(filename, float, 'w+', shape=self.shape)
            for row, record in enumerate(self):
                array[row,:] = record
        else:
            values = chain.from_iterable(self)
            count = np.prod(self.shape) 
            array = np.fromiter(values, float, count).reshape(self.shape)
        return array 

    def to_array(self, filename=None):
        """Wrapper for to_ndarray and to_structured_array. Returns an ndarray if the
        dataset is all-numeric homogeneous (and no datetimes), a structured
        array otherwise"""
        if self.is_homogeneous:
            return self.to_ndarray(filename)
        else:
            return self.to_structured_array(filename)



if __name__ == "__main__":
    import time
    from contextlib import closing
    savFileName = "./test_data/all_numeric_datetime_uncompressed.sav"
    kwargs = dict( \
    savFileName = savFileName,
    varNames = ["v1", "v2"],
    varTypes = {"v1": 0, "v2": 0},
    formats = {"v1": "DOLLAR15.2", "v2": "EDATE40"} )
    if not os.path.exists(savFileName):
        with SavWriter(**kwargs) as writer:
            for i in xrange(10 ** 2):
                value = None if not i else 11654150400.
                writer.writerow([i, value])

    klass = globals()[sys.argv[1]]
    start = time.time() 
    filename = "./test_data/Employee data.sav"
    filename = "./test_data/greetings.sav"
    #filename = "./test_data/all_numeric_datetime_uncompressed.sav"
    #filename = "/home/albertjan/nfs/Public/somefile_uncompressed.sav" 
    #filename = '/home/antonia/Desktop/big.sav'
    #filename = '/home/albertjan/nfs/Public/bigger.sav'
    with closing(klass(filename, rawMode=False, ioUtf8=True)) as sav:
        #print(sav.struct_dtype.descr)
        #array = sav.to_ndarray() #"/tmp/test.dat")
        array = sav.to_structured_array() 
        #print(sav.formats)
        #sav.all()
        #for record in sav:
            #print(record)
            #pass  
    print("%s version: %5.3f" % (sys.argv[1], (time.time() - start)))


