#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *
import os
import operator
import locale
import datetime
import collections
import functools

from savReaderWriter import *
from header import *
from helpers import *

@rich_comparison
@implements_to_string
class SavReader(Header):
    """ Read SPSS system files (.sav, .zsav)

    Parameters
    ---------- 
    savFileName : str
        the file name of the spss data file
    returnHeader : bool
        indicates whether the first record should be a list of variable names
    recodeSysmisTo: (value)
        indicates to which value missing values should be recoded
    selectVars : list
        indicates which variables in the file should be selected.
        The variables should be specified as a list of valid variable names.
        If ``None`` is specified, all the variables in the file are used
    idVar : str
        indicates which variable in the file should be used for use as id
        variable for the 'get' method
    verbose : bool
        indicates whether information about the spss data file (e.g., number
        of cases, variable names, file size) should be printed on the screen.
    rawMode : bool
        indicates whether values should get SPSS-style formatting, and whether
        date variables (if present) should be converted into ISO-dates. If set
        to ``True`` the program does not format any values, which increases 
        processing speed. In particular ``rawMode=True`` implies that:

        * SPSS datetimes will not be converted into ISO8601 dates
        * SPSS `N` formats will not be converted into strings with leading zeroes
        * SPSS `$sysmis` values will not be converted into ``None`` values
        * String values will be ceiled multiples of 8 bytes
        See also :ref:`formats` and :ref:`dateformats`
    ioUtf8 : bool
        indicates the mode in which text communicated to or from the I/O 
        Module will be. Valid values are True (UTF-8 mode aka Unicode mode)
        and False (Codepage mode). Cf. `SET UNICODE=ON/OFF`.
        See also under :py:meth:`savReaderWriter.Generic.ioUtf8` and under
        ``ioUtf8`` in :py:class:`savReaderWriter.SavWriter`.
    ioLocale : locale str
        indicates the locale of the I/O module. Cf. `SET LOCALE` (default
        = ``None``, which corresponds to 
        ``locale.setlocale(locale.LC_CTYPE)``, for example: 
        ``en_US.UTF-8`` (Unix) or ``english`` (Windows).
        See also under :py:meth:`savReaderWriter.Generic.ioLocale`. 

    Examples
    --------
    Typical use:

    .. code-block:: python

        with SavReader('somefile.sav', returnHeader=True) as reader:
            header = next(reader)
            for line in reader:
                process(line)
    """

    def __init__(self, savFileName, returnHeader=False, recodeSysmisTo=None,
                 verbose=False, selectVars=None, idVar=None, rawMode=False,
                 ioUtf8=False, ioLocale=None):
        """ Constructor. Initializes all vars that can be recycled """
        super(SavReader, self).__init__(savFileName, b"rb", None,
                                        ioUtf8, ioLocale)
        self.savFileName = savFileName
        self.returnHeader = returnHeader
        self.recodeSysmisTo = recodeSysmisTo
        self.verbose = verbose
        self.selectVars = selectVars
        self.idVar = idVar
        self.rawMode = rawMode

        self.header = self.getHeader(self.selectVars)
        self.bareformats, self.varWids = self._splitformats()
        self.autoRawMode = self._isAutoRawMode()

        self.ioUtf8_ = ioUtf8
        self.sysmis_ = self.sysmis
        self.numVars = self.numberofVariables
        self.nCases = self.numberofCases

        self.myStruct = self.getStruct(self.varTypes, self.varNames)
        self.unpack_from = self.myStruct.unpack_from
        self.seekNextCase = self.spssio.spssSeekNextCase
        self.caseBuffer = self.getCaseBuffer()

    def __enter__(self):
        """ This function opens the spss data file (context manager)."""
        if self.verbose and self.ioUtf8_:
            print(self.replace(os.linesep, "\n"))
        elif self.verbose:
            print(str(self).replace(os.linesep, "\n"))
        return iter(self)

    def __exit__(self, type, value, tb):
        """ This function closes the spss data file and does some cleaning.

        .. warning::

            Always ensure the the .sav file is properly closed, either by
            using a context manager (``with`` statement) or by using 
            ``close()``"""
        if type is not None:
            pass  # Exception occurred
        self.close()

    def close(self):
        """This function closes the spss data file and does some cleaning."""
        if not segfaults:
            self.closeSavFile(self.fh, mode=b"rb")
        del self.spssio
        try:
            locale.resetlocale()  # fails on Windows
        except:
            locale.setlocale(locale.LC_ALL, "")

    def __len__(self):
        """ This function reports the number of cases (rows) in the spss data
        file. For example: len(SavReader(savFileName))"""
        return self.nCases

    # Python 3: see @rich_comparison class decorator
    def __cmp__(self, other):
        """ This function implements behavior for all of the comparison
        operators so comparisons can be made between SavReader instances,
        or comparisons between SavReader instances and integers."""
        if not isinstance(other, (SavReader, int)):
            raise TypeError
        other = other if isinstance(other, int) else len(other)
        if len(self) < other:
            return -1
        elif len(self) == other:
            return 0
        else:
            return 1

    def __hash__(self):
        """This function returns a hash value for the object to ensure it
        is hashable."""
        return id(self)

    def __str__(self):
        """This function returns a conscise file report of the spss data file
        For example::
            data = SavReader(savFileName)
            print(str(data))  # Python 3: bytes(data)
            data.close()"""
        return self.__unicode__().encode(self.fileEncoding)

    def __unicode__(self):
        """This function returns a conscise file report of the spss data file.
        For example::
            data = SavReader(savFileName)
            print(unicode(data))  # Python 3: str(data)
            data.close()"""
        return self.getFileReport()

    @memoized_property
    def shape(self):
        """This function returns the number of rows (nrows) and columns
        (ncols) as a namedtuple. For example::
            data = SavReader(savFileName)
            data.shape.nrows == len(data) # True
            data.close()"""
        shape = (self.nCases, self.numVars)
        return collections.namedtuple("Shape", "nrows ncols")(*shape)

    def _isAutoRawMode(self):
        """Helper function for formatValues function. Determines whether
        iterating over each individual value is really needed"""
        hasDates = bool(set(self.bareformats.values()) & set(supportedDates))
        hasNfmt = b"N" in list(self.bareformats.values())
        hasRecodeSysmis = self.recodeSysmisTo is not None
        items = [hasDates, hasNfmt, hasRecodeSysmis, self.ioUtf8_]
        return False if any(items) else True

    # TODO: turn this into a decorator
    def formatValues(self, record):
        """This function formats date fields to ISO dates (yyyy-mm-dd), plus
        some other date/time formats. The SPSS N format is formatted to a
        character value with leading zeroes. System missing values are recoded
        to <recodeSysmisTo>. If rawMode==True, this function does nothing"""
        if self.rawMode or self.autoRawMode:
            return record  # 6-7 times faster!
        for i, value in enumerate(record):
            varName = self.header[i]
            varType = self.varTypes[varName]
            bareformat_ = self.bareformats[varName]
            varWid = self.varWids[varName]
            if varType == 0:
                # recode system missing values, if present and desired
                if value > self.sysmis_:
                    pass
                else:
                    record[i] = self.recodeSysmisTo
                # format N-type values (=numerical with leading zeroes)
                if bareformat_ in (b"N", u"N"):
                    #record[i] = str(value).zfill(varWid)
                    nfmt_value = "%%0%dd" % varWid % value  #15 x faster (zfill)
                    nfmt_value = nfmt_value if self.ioUtf8 == 1 else bytez(nfmt_value)
                    record[i] = nfmt_value  #15 x faster (zfill)
                # convert SPSS dates to ISO dates
                elif bareformat_ in supportedDates:
                    fmt = supportedDates[bareformat_]
                    args = (value, fmt, self.recodeSysmisTo)
                    record[i] = self.spss2strDate(*args)
                    if bareformat_ == b"QYR" and record[i]:
                        # convert month to quarter, e.g. 12 Q 1990 --> 4 Q 1990
                        # There is no such thing as a %q strftime directive
                        try:
                            record[i] = QUARTERS[record[i][:2]] + record[i][2:]
                        except (KeyError, TypeError):
                            record[i] = self.recodeSysmisTo
            elif varType > 0:
                value = value[:varType]
                if self.ioUtf8_:
                    record[i] = value.decode("utf-8")
                else:
                    record[i] = value
        return record

    def _items(self, start=0, stop=None, step=1, returnHeader=False):
        """ This is a helper function to implement the __getitem__ and
        the __iter__ special methods. """

        if returnHeader:
            yield self.header

        used_as_iterator = all([start == 0, stop is None, step == 1])
        if not used_as_iterator:
            retcode = self.seekNextCase(c_int(self.fh), c_long(0))  # reset
            if retcode:
                checkErrsWarns("Problem seeking first case", retcode)

        stop = self.nCases if stop is None else stop
        selection = self.selectVars is not None
        selectOne = len(self.selectVars) == 1 if self.selectVars else None

        for case in xrange(start, stop, step):
            if start or step != 1:
                # only call this when iterating over part of the records
                retcode = self.seekNextCase(c_int(self.fh), c_long(case))
                if retcode:
                    checkErrsWarns("Problem seeking case %d" % case, retcode)

            record = self.record
            if selection:
                record = self.selector(record)
                record = [record] if selectOne else list(record)

            yield self.formatValues(record)

    def __iter__(self):
        """x.__iter__() <==> iter(x). Yields records as a list. 
        For example::
        
            with SavReader("someFile.sav") as reader:
                for line in reader:
                    process(line)"""
        return self._items(0, None, 1, self.returnHeader)

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y], where y may be int or slice.
        This function reports the record of case number <key>.
        The <key> argument may also be a slice, for example::
            
            data = SavReader("someFile.sav") 
            print("The first six records look like this: %s" % data[:6])
            print("The first record looks like this: %s" % data[0])
            print("First column: %s" % data[..., 0]) # requires numpy
            print("Row 4 & 5, first three cols: %s" % data[4:6, :3])
            data.close()"""

        is_slice = isinstance(key, slice)
        is_array_slice = key is Ellipsis or isinstance(key, tuple)

        if is_slice:
            start, stop, step = key.indices(self.nCases)
        elif is_array_slice:
            return self._get_array_slice(key, self.nCases, len(self.header))
        else:
            key = operator.index(key)
            start = key + self.nCases if key < 0 else key
            if not 0 <= start < self.nCases:
                raise IndexError("Index out of bounds")
            stop = start + 1
            step = 1

        records = self._items(start, stop, step)
        if is_slice:
            return list(records)
        return next(records)

    def _cast_array(self, cstart, cstop, cstep, raw_result):
        """Helper for _get_array_slice function"""
        varNames = self.varNames[slice(cstart, cstop, cstep)]
        numVars = [v for v in varNames if self.varTypes[v] == 0 and not 
                   re.search(b"time|date|n\d+", self.formats[v], re.I)]
        return [[float(item) if v in numVars else item for 
                v, item in zip(varNames, record)]for record in raw_result]

    def _get_array_slice(self, key, nRows, nCols):
        """This is a helper function to implement array slicing with numpy"""
        if not numpyOk:
            raise ImportError("Array slicing requires the numpy library")

        is_index = False
        rstart = cstart = 0
        cstop = cstep = None

        try:
            row, col = key
            if isinstance(row, int) and row < 0:
                row = nRows + row
            if isinstance(col, int) and col < 0:
                col = nCols + col

            ## ... slices
            if isinstance(row, slice) and col is Ellipsis:
                # reader[1:2, ...]
                rstart, rstop, rstep = row.indices(nRows)
                cstart, cstop, cstep = 0, nRows, 1
            elif row is Ellipsis and isinstance(col, slice):
                # reader[..., 1:2]
                rstart, rstop, rstep = 0, nRows, 1
                cstart, cstop, cstep = col.indices(nCols)
            elif isinstance(row, slice) and isinstance(col, slice):
                # reader[1:2, 1:2]
                rstart, rstop, rstep = row.indices(nRows)
                cstart, cstop, cstep = col.indices(nCols)
            elif row is Ellipsis and col is Ellipsis:
                # reader[..., ...]
                # DeprecationWarning in recent numpy versions
                rstart, rstop, rstep = 0, nRows, 1
                cstart, cstop, cstep = 0, nCols, 1

            ## ... indexes
            elif isinstance(row, int) and col is Ellipsis:
                # reader[1, ...]
                rstart, rstop, rstep = row, row + 1, 1
                cstart, cstop, cstep = 0, nCols, 1
                is_index = True
            elif row is Ellipsis and isinstance(col, int):
                # reader[..., 1]
                rstart, rstop, rstep = 0, nRows, 1
                cstart, cstop, cstep = col, col + 1, 1
                is_index = True
            elif  isinstance(row, int) and isinstance(col, int):
                # reader[1, 1]
                rstart, rstop, rstep = row, row + 1, 1
                cstart, cstop, cstep = col, col + 1, 1
                is_index = True

            # ... slice + index
            elif isinstance(row, slice) and isinstance(col, int):
                # reader[1:2, 1]
                rstart, rstop, rstep = row.indices(nRows)
                cstart, cstop, cstep = col, col + 1, 1
            elif isinstance(row, int) and isinstance(col, slice):
                # reader[1, 1:2]
                rstart, rstop, rstep = row, row + 1, 1
                cstart, cstop, cstep = col.indices(nCols)
            try:
                if not 0 <= abs(rstart) < nRows:
                    raise IndexError("Index out of bounds")
                if not 0 <= abs(cstart) < nCols:
                    raise IndexError("Index out of bounds")
                key = (Ellipsis, slice(cstart, cstop, cstep))

            except UnboundLocalError:
                msg = "The array index is either invalid, or not implemented"
                raise TypeError(msg)

        except TypeError:
            # reader[...]
            rstart, rstop, rstep = 0, nRows, 1
            key = (Ellipsis, Ellipsis)

        # select the rows, cols respectively
        records = self._items(rstart, rstop, rstep)
        raw_result = numpy.array(list(records))[key].tolist()

        # cast the result, so floats become floats again
        result = self._cast_array(cstart, cstop, cstep, raw_result)

        # flatten list if it's row or one col                 
        if abs(key[1].start - key[1].stop) == 1 or len(result) == 1:
            return functools.reduce(list.__add__, result) 

        if is_index:
            return result[0]
        return result

    def head(self, n=5):
        """ This convenience function returns the first <n> records.
        Example::

            data = SavReader("someFile.sav") 
            print("The first five records look like this: %s" % data.head())
            data.close()"""
        return self[:abs(n)]

    def tail(self, n=5):
        """ This convenience function returns the last <n> records.
        Example::

            data = SavReader("someFile.sav") 
            print("The last four records look like this: %s" % data.tail(4))
            data.close()"""
        return self[-abs(n):]

    def all(self):
        """ This convenience function returns all the records.
        Example::

            data = SavReader("someFile.sav") 
            list_of_lists = data.all()
            data.close()"""
        return [record for record in iter(self)]

    def __contains__(self, item):
        """ This function implements membership testing and returns True if
        <idVar> contains <item>. Thus, it requires the 'idVar' parameter to
        be set.
        Example::

            reader = SavReader(savFileName, idVar="ssn")
            "987654321" in reader # returns True or False
        """
        return bool(self.get(item))

    def get(self, key, default=None, full=False):
        """ This function returns the records for which <idVar> == <key>
        if <key> in <savFileName>, else <default>. Thus, the function mimics
        dict.get, but note that dict[key] is NOT implemented. NB: Even though
        this uses a binary search, this is not very fast on large data (esp.
        the first call, and with full=True)

        Parameters
        ----------
        key : str, int, float
            key for which the corresponding record should be returned
        default : (value)
            value that should be returned if <key> is not found
        full : bool
            value that indicates whether *all* records for which
            <idVar> == <key> should be returned

        Examples
        --------
        For example::

            data = SavReader(savFileName, idVar="ssn")
            data.get("987654321", "social security number not found!")
            data.close()"""

        if not self.idVar in self.varNames:
            msg = ("SavReader object must be instantiated with an existing " +
                   "variable as an idVar argument")
            raise NameError(msg)

        #two slightly modified functions from the bisect module
        def bisect_right(a, x, lo=0, hi=None):
            if hi is None:
                hi = len(a)
            while lo < hi:
                mid = (lo + hi) // 2
                if x < a[mid][0]:
                    hi = mid  # a[mid][0], not a[mid]
                else:
                    lo = mid + 1
            return lo

        def bisect_left(a, x, lo=0, hi=None):
            if hi is None:
                hi = len(a)
            while lo < hi:
                mid = (lo + hi) // 2
                if a[mid][0] < x:
                    lo = mid + 1  # a[mid][0], not a[mid]
                else:
                    hi = mid
            return lo

        idPos = self.varNames.index(self.idVar)
        if not hasattr(self, "isSorted"):
            self.isSorted = True
            if self.varTypes[self.idVar] == 0:
                if not isinstance(key, (int, float)):
                    return default
                self.recordz = ((record[idPos], i) for i,
                                record in enumerate(iter(self)))
            else:
                if not isinstance(key, basestring):
                    return default
                self.recordz = ((record[idPos].rstrip(), i) for i,
                                record in enumerate(iter(self)))
            self.recordz = sorted(self.recordz)
        insertLPos = bisect_left(self.recordz, key)
        insertRPos = bisect_right(self.recordz, key)
        if full:
            result = [self[record[1]] for record in
                      self.recordz[insertLPos: insertRPos]]
        else:
            if insertLPos == insertRPos:
                return default
            result = self[self.recordz[insertLPos][1]]
        if result:
            return result
        return default

    def getSavFileInfo(self):
        """ This function reads and returns some basic information of the open
        spss data file."""
        return (self.numVars, self.nCases, self.varNames, self.varTypes,
                self.formats, self.varLabels, self.valueLabels)

    def decode(func):
        """Decorator to decode datestrings for ioUtf8"""
        @functools.wraps(func)
        def wrapper(*args):
            value = func(*args)
            self = args[0]
            if not self.ioUtf8 or self.ioUtf8 == 2:
                return value  # unchanged
            try:
                return value.decode("utf-8")
            except AttributeError:
                return value
        return wrapper

    @memoize
    @decode
    def spss2strDate(self, spssDateValue, fmt, recodeSysmisTo):
        """This function converts internal SPSS dates (number of seconds
        since midnight, Oct 14, 1582 (the beginning of the Gregorian calendar))
        to a human-readable format (ISO-8601 where possible)

        Parameters
        ----------
        spssDateValue : int, float
        fmt : strptime format
        recodeSysmisTo : what SPSS $sysmis values will be replaced with

        Examples
        --------
        For example::

            data = SavReader(savFileName)
            iso_date = data.spss2strDate(11654150400.0, "%Y-%m-%d", None)
            data.close()

        See also
        --------
        savReaderWriter.SavReaderNp.spss2datetimeDate : returns 
            ``datetime.datetime`` object
        strptime-formats-settings
            :download:`__init__.py <../__init__.py>` to change the 
            strptime formats from ISO into something else. Note that dates 
            before 1900 require the mx package, which is Python 2 only (2015).
 
        :ref:`dateformats` : overview of SPSS datetime formats"""
        try:
            MIDNIGHT_OCT_14_1582 = 86400
            time_only = spssDateValue < MIDNIGHT_OCT_14_1582
            is_time_fmt = fmt.startswith("%H:%M:%S") and time_only
            is_dtime_fmt = fmt == "%d %H:%M:%S"
            is_normal_fmt = not is_time_fmt and not is_dtime_fmt 
            delta = datetime.timedelta(seconds=spssDateValue)
            gregorianEpoch = datetime.datetime(1582, 10, 14, 0, 0, 0)
            theDate = (gregorianEpoch + delta)

            if theDate.year >= 1900 and is_normal_fmt:
                return bytez(datetime.datetime.strftime(theDate, fmt))
            elif is_normal_fmt:  # pre 1900: requires mx; no Python 3 and pypy
                import mx.DateTime
                return mx.DateTime.DateTimeFrom(theDate).strftime(fmt)
            elif is_time_fmt:
                return bytez(str(delta).zfill(8))
            elif is_dtime_fmt: 
                time_part = bytez(theDate.isoformat().split("T")[1])
                day_part = bytez(str(delta.days).zfill(2))
                return day_part + b" " + time_part
            else:
                raise RuntimeError
        except (OverflowError, TypeError, ValueError):
            return recodeSysmisTo

    def getFileReport(self):
        """ This function prints a report about basic file characteristics """
        filesize = os.path.getsize(self.savFileName)
        kb = float(filesize) / 2**10
        mb = float(filesize) / 2**20
        (fileSize, label) = (mb, "MB") if mb > 1 else (kb, "kB")
        systemString = self.systemString.decode(self.fileEncoding)
        spssVersion = ".".join(map(str, self.spssVersion))
        lang, cp = locale.getlocale()
        intEnc = "Utf-8/Unicode" if self.ioUtf8 else "Codepage (%s)" % cp
        varlist = []
        line = "  %%0%sd. %%s (%%s - %%s)" % len(str(len(self.varNames) + 1))
        for cnt, varName in enumerate(self.varNames):
            lbl = "string" if self.varTypes[varName] > 0 else "numerical"
            format_ = self.formats[varName].decode(self.fileEncoding)
            varName = varName.decode(self.fileEncoding) 
            varlist.append(line % (cnt + 1, varName, format_, lbl))
        info = {"savFileName": self.savFileName,
                "fileSize": fileSize,
                "label": label,
                "nCases": self.nCases,
                "nCols": len(self.varNames),
                "nValues": self.nCases * len(self.varNames),
                "spssVersion": "%s (%s)" % (systemString, spssVersion),
                "ioLocale": self.ioLocale.decode(self.fileEncoding),
                "ioUtf8": intEnc,
                "fileEncoding": self.fileEncoding,
                "fileCodePage": self.fileCodePage,
                "isCompatible": "Yes" if self.isCompatibleEncoding() else "No",
                "local_language": lang,
                "local_encoding": cp,
                "varlist": os.linesep.join(varlist),
                "sep": os.linesep,
                "asterisks": 70 * "*"}
        report = ("%(asterisks)s%(sep)s" +
                  "*File '%(savFileName)s' (%(fileSize)3.2f %(label)s) has " +
                  "%(nCols)s columns (variables) and %(nCases)s rows " +
                  "(%(nValues)s values)%(sep)s" +
                  "*The file was created with SPSS version: %(spssVersion)s%" +
                  "(sep)s" +
                  "*The interface locale is: '%(ioLocale)s'%(sep)s" +
                  "*The interface mode is: %(ioUtf8)s%(sep)s" +
                  "*The file encoding is: '%(fileEncoding)s' (Code page: " +
                  "%(fileCodePage)s)%(sep)s" +
                  "*File encoding and the interface encoding are compatible:" +
                  " %(isCompatible)s%(sep)s" +
                  "*Your computer's locale is: '%(local_language)s' (Code " +
                  "page: %(local_encoding)s)%(sep)s" +
                  "*The file contains the following variables:%(sep)s" +
                  "%(varlist)s%(sep)s%(asterisks)s%(sep)s") % info
        if hasattr(report, "decode"):
            report = report.decode(self.fileEncoding)
        return report

    def getHeader(self, selectVars):
        """This function returns the variable names, or a selection thereof
        (as specified as a list using the selectVars parameter), as a list."""
        if selectVars is None:
            header = self.varNames
        elif isinstance(selectVars, (list, tuple)):
            diff = set(selectVars).difference(set(self.varNames))
            if diff:
                msg = "Variable names misspecified (%r)" % ", ".join(diff)
                raise NameError(msg)
            varPos = [self.varNames.index(v) for v in self.varNames
                      if v in selectVars]
            self.selector = operator.itemgetter(*varPos)
            header = self.selector(self.varNames)
            header = [header] if not isinstance(header, tuple) else list(header)
        else:
            msg = ("Variable names list misspecified. Must be 'None' or a "
                   "list or tuple of existing variables")
            raise TypeError(msg)
        return header
