#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *
import os
import time

from savReaderWriter import *
from py3k import *
from header import *

if cWriterowOK and not isPy3k:
    cWriterow = cWriterow.cWriterow

class SavWriter(Header):

    """ Write SPSS system files (.sav, .zsav)

    Below, the associated SPSS commands are given in `CAPS`.

    Parameters
    ----------

    savFileName : str
        The file name of the spss data file.

        * File names that end with '.sav' are compressed using the 'old' 
          compression scheme
        * File names that end with '_uncompressed.sav' are, well, not 
          compressed. This is useful when you intend to read the files with 
          the faster :py:class:`savReaderWriter.SavReaderNp` class
        * File names that end with '.zsav' are compressed using the ZLIB 
          (ZSAV) compression scheme (requires v21 SPSS I/O files)
    varNames : list
        list of of strings of the variable names in the order in which they
        should appear in the spss data file. See also under 
        :py:meth:`savReaderWriter.Header.varNamesTypes`
    varTypes : dict
        varTypes dictionary `{varName: varType}`

        * varType == 0 --> numeric
        * varType > 0 --> character' of that length (in bytes!)
        See also under :py:meth:`savReaderWriter.Header.varNamesTypes`

    valueLabels : dict, optional
        value label dictionary `{varName: {value: label}}` Cf. `VALUE LABELS`
    varLabels : dict, optional
        variable label dictionary `{varName: varLabel}`. Cf. `VARIABLE LABEL`.
        See also under :py:meth:`savReaderWriter.Header.varLabels`
    formats : dict, optional
        format dictionary `{varName: printFmt}` Cf. `FORMATS`.
        See also under :py:meth:`savReaderWriter.Header.formats`, under
        :ref:`formats` and under :ref:`dateformats`
    missingValues : dict, optional
        missing values dictionary `{varName: {missing value spec}}`.
        Cf. `MISSING VALUES`. See also under 
        :py:meth:`savReaderWriter.Header.missingValues`

    measureLevels : dict, optional
        measurement level dictionary `{varName: <level>}`
        Valid levels are: "unknown", "nominal", "ordinal", "scale",
        "ratio", "flag", "typeless". Cf. `VARIABLE LEVEL`
        See also under :py:meth:`savReaderWriter.Header.measureLevels`

        .. warning::
            `measureLevels`, `columnWidths` and `alignments` must all three
            be set, if used
    columnWidths : dict, optional
        column display width dictionary `{varName: <int>}`.
        Cf. `VARIABLE WIDTH`. (default: None --> >= 10 [stringVars] or 
        automatic [numVars])
        See also under :py:meth:`savReaderWriter.Header.columnWidths`
    alignments : dict, optional
        variable alignment dictionary `{varName: <left/center/right>}`
        Cf. `VARIABLE ALIGNMENT` (default: None --> left)
        See also under :py:meth:`savReaderWriter.Header.alignments`

    varSets : dict, optional
        sets dictionary `{setName: list_of_valid_varNames}`. 
        Cf. `SETSMR` command.
        See also under :py:meth:`savReaderWriter.Header.varSets`
    varRoles : dict, optional
        variable roles dictionary `{varName: varRole}`, where varRole
        may be any of the following: 'both', 'frequency', 'input', 'none',
        'partition', 'record ID', 'split', 'target'. Cf. `VARIABLE ROLE`
        See also under :py:meth:`savReaderWriter.Header.varRoles`
    varAttributes : dict, optional
        variable attributes dictionary `{varName: {attribName:
        attribValue}`. Cf. `VARIABLE ATTRIBUTES`.
        See also under :py:meth:`savReaderWriter.Header.varAttributes`
    fileAttributes : dict, optional
        file attributes dictionary `{attribName: attribValue}`.
        Cf. FILE ATTRIBUTES. See also under 
        :py:meth:`savReaderWriter.Header.fileAttributes`
    fileLabel : dict, optional 
        file label string, which defaults to "File created by user
        <username> at <datetime>" is file label is None. Cf. `FILE LABEL`
        See also under :py:meth:`savReaderWriter.Header.fileLabel`
    multRespDefs : dict, optional
        multiple response sets definitions (dichotomy groups or
        category groups) dictionary `{setName: <set definition>}`. In SPSS 
        syntax, 'setName' has a dollar prefix ('$someSet'). Cf. `MRSETS`.
        See also under :py:meth:`savReaderWriter.Header.multRespDefs`

    caseWeightVar : str, optional
        valid varName that is set as case weight (cf. `WEIGHT BY`)
        See also under :py:meth:`savReaderWriter.Header.caseWeightVar`
    overwrite : bool, optional
        indicates whether an existing SPSS file should be overwritten
    ioUtf8 : bool, optional
        indicates the mode in which text communicated to or from the
        I/O Module will be. Valid values are True (UTF-8/unicode mode, cf. 
        `SET UNICODE=ON`) or False (Codepage mode, `SET UNICODE=OFF`).
        See also under :py:meth:`savReaderWriter.Generic.ioUtf8`

    ioLocale : bool, optional
        indicates the locale of the I/O module, cf. `SET LOCALE` (default:
        None, which is the same as ``".".join(locale.getlocale())``.
        See also under :py:meth:`savReaderWriter.Generic.ioLocale`
    mode : str, optional
      indicates the mode in which <savFileName> should be opened. Possible
      values are:

      * "wb" --> write
      * "ab" --> append
      * "cp" --> copy: initialize header using ``refSavFileName`` as a reference
        file, cf. `APPLY DICTIONARY`.
    refSavFileName : str, optional
      reference file that should be used to initialize the header (aka the 
      SPSS data dictionary) containing variable label, value label, missing
      value, etc. etc. definitions. Only relevant in conjunction with 
      ``mode="cp"``.
   
    See also
    --------

    savReaderWriter.Header : for details about how to define individual 
        metadata items

    Examples
    --------

    Typical use::

        records = [[b'Test1', 1, 1], [b'Test2', 2, 1]]
        varNames = [b'var1', b'v2', b'v3']
        varTypes = {b'var1': 5, b'v2': 0, b'v3': 0}
        savFileName = 'someFile.sav'
        with SavWriter(savFileName, varNames, varTypes) as writer:
            for record in records:
                writer.writerow(record)
    """
    def __init__(self, savFileName, varNames, varTypes, valueLabels=None,
                 varLabels=None, formats=None, missingValues=None,
                 measureLevels=None, columnWidths=None, alignments=None,
                 varSets=None, varRoles=None, varAttributes=None,
                 fileAttributes=None, fileLabel=None, multRespDefs=None,
                 caseWeightVar=None, overwrite=True, ioUtf8=False, 
                 ioLocale=None, mode=b"wb", refSavFileName=None):
        """ Constructor. Initializes all vars that can be recycled """
        super(Header, self).__init__(savFileName, ioUtf8, ioLocale)
        self.savFileName = savFileName
        self.varNames = self.encode(varNames)
        self.varTypes = self.encode(varTypes)
        self.overwrite = overwrite
        self.mode = mode
        self.refSavFileName = refSavFileName

        self.fh = super(Header, self).openSavFile(self.savFileName, self.mode,
                                                  self.refSavFileName)
        self.myStruct = self.getStruct(self.varTypes, self.varNames, self.mode)
        self.pack_into = self.myStruct.pack_into

        self.sysmis_ = self.sysmis
        self.ioUtf8_ = ioUtf8
        self.pad_8_lookup = self._getPaddingLookupTable(self.varTypes)
        self.pad_string = self._pyWriterow_pad_string(isPy3k)
        self.bytify = bytify(self.fileEncoding)  # from py3k module

        if self.mode == b"wb":
            self._openWrite(self.savFileName, self.overwrite)
            self.varNamesTypes = self.varNames, self.varTypes
            self.valueLabels = valueLabels
            self.varLabels = varLabels
            self.formats = formats
            self.missingValues = missingValues
            self.measureLevels = measureLevels
            self.columnWidths = columnWidths
            self.alignments = alignments
            self.varSets = varSets
            self.varRoles = varRoles
            self.varAttributes = varAttributes
            self.fileAttributes = fileAttributes
            self.fileLabel = fileLabel
            self.multRespDefs = multRespDefs
            self.caseWeightVar = caseWeightVar
            #self.dateVariables = dateVariables
            triplet = [measureLevels, columnWidths, alignments]
            if all([item is None for item in triplet]):
                self._setColWidth10()
            self.textInfo = self.savFileName
        if self.mode in (b"wb", b"cp"):
            self._commitHeader()
        self.caseBuffer = self.getCaseBuffer()

    def __enter__(self):
        """This function returns the writer object itself so the writerow and
        writerows methods become available for use with 'with' statements"""
        return self

    def __exit__(self, type, value, tb):
        """ This function closes the spss data file.

        .. warning::

            Always ensure the the .sav file is properly closed, either by 
            using a context manager (``with`` statement) or by using 
            ``close()``"""
        if type is not None:
            pass  # Exception occurred
        self.closeSavFile(self.fh, self.mode)

    def _openWrite(self, savFileName, overwrite):
        """ This function opens a file in preparation for creating a new IBM
        SPSS Statistics data file"""
        if os.path.exists(savFileName) and not os.access(savFileName, os.W_OK):
            raise IOError("No write access for file %r" % savFileName)

        if overwrite or not os.path.exists(savFileName):
            if savFileName.lower().endswith(".zsav"):
                self.fileCompression = b"zlib"  # only with v21 libraries!
            elif savFileName.lower().endswith("_uncompressed.sav"):
                self.fileCompression = b"uncompressed"
            else:
                self.fileCompression = b"standard"
        elif not overwrite and os.path.exists(savFileName):
            raise IOError("File %r already exists!" % savFileName)

    def convertDate(self, day, month, year):
        """This function converts a Gregorian date expressed as day-month-year
        to the internal SPSS date format. The time portion of the date variable
        is set to 0:00. To set the time portion if the date variable to another
        value, use convertTime."""
        func = self.spssio.spssConvertDate
        func.argtypes = [c_int, c_int, c_int, POINTER(c_double)]
        spssDate = c_double()
        retcode = func(day, month, year, spssDate)
        if retcode:
            msg = "Problem converting date value '%s-%s-%s'" % (day, month, year)
            checkErrsWarns(msg, retcode)
        return spssDate.value

    def convertTime(self, day, hour, minute, second):
        """This function converts a time given as day, hours, minutes, and
        seconds to the internal SPSS time format."""
        d, h, m, s, spssTime = (c_int(day), c_int(hour), c_int(minute),
                                c_double(float(second)), c_double())
        retcode = self.spssio.spssConvertTime(d, h, m, s, byref(spssTime))
        if retcode:
            msg = "Problem converting time value '%s %s:%s:%s'"
            checkErrsWarns(msg % (day, hour, minute, second), retcode)
        return spssTime.value

    def spssDateTime(self, datetimeStr=b"2001-12-08", strptimeFmt="%Y-%m-%d"):
        """ This function converts a date/time string into an SPSS date,
        using a strptime format. See also :ref:`dateformats`"""
        try:
            datetimeStr = datetimeStr.decode("utf-8")
            dt = time.strptime(datetimeStr, strptimeFmt)
        except (ValueError, TypeError, AttributeError):
            return self.sysmis
        day, month, year = dt.tm_mday, dt.tm_mon, dt.tm_year
        hour, minute, second = dt.tm_hour, dt.tm_min, dt.tm_sec
        return (self.convertDate(day, month, year) +
                self.convertTime(0, hour, minute, second))

    def _commitHeader(self):
        """This function writes the data dictionary to the data file associated
        with file handle 'fh'. Before any case data can be written, the
        dictionary must be committed; once the dictionary has been committed,
        no further changes can be made to it."""
        retcode = self.spssio.spssCommitHeader(c_int(self.fh))
        if retcode:
            checkErrsWarns("Problem committing header", retcode)

    def _getPaddingLookupTable(self, varTypes):
        """Helper function that returns a lookup table that maps string lengths
        to string lengths to the nearest ceiled multiple of 8. For example:
        {1:%-8s, 7:%-8s, 9: %-16s, 24: %-24s}. Purpose: Get rid of trailing
        null bytes"""
        strLengths = varTypes.values()
        if isPy3k:
            return dict([(i, (-8 * (i // -8))) for i in strLengths])
        return dict([(i, "%%-%ds" % (-8 * (i // -8))) for i in strLengths])

    def _pyWriterow_pad_string(self, isPy3k):
        """Helper that returns a function to pad string values using
        _getPaddingLookupTable. Padding is done differently for Python 2 and
        3 (probably the latter is slower)"""
        if isPy3k:
            def _padStringValue(value, varType):
                # % replacement is not possible with bytes
                return value.ljust(self.pad_8_lookup[varType])
        else:
            def _padStringValue(value, varType):
                # Get rid of trailing null bytes --> 7 x faster than 'ljust'
                return self.pad_8_lookup[varType] % value
        return _padStringValue

    def _pyWriterow(self, record):
        """ This function writes one record, which is a Python list,
        compare this Python version with the Cython version cWriterow."""
        float_ = float
        encoding = self.fileEncoding
        pad_string = self.pad_string
        for i, value in enumerate(record):
            varName = self.varNames[i]
            varType = self.varTypes[varName]
            if varType == 0:
                try:
                    value = float_(value)
                except (ValueError, TypeError):
                    value = self.sysmis_
            else:
                value = pad_string(value, varType)
                if self.ioUtf8_ and isinstance(value, unicode):
                    value = value.encode("utf-8")
            record[i] = value
        self.record = record

    def writerow(self, record):
        """This function writes one record, which is a Python list."""
        if cWriterowOK:
            cWriterow(self, record)
            return
        self._pyWriterow(record)

    def writerows(self, records):
        """ This function writes all records."""
        for record in records:
            self.writerow(record)
