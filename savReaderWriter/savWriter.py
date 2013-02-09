#!/usr/bin/env python
# -*- coding: utf-8 -*-

from savReaderWriter import *
from header import *
if cWriterowOK:
    cWriterow = cWriterow.cWriterow

class SavWriter(Header):

    """ Write Spss system files (.sav, .zsav)

    Parameters:
    * Formal
    -savFileName: the file name of the spss data file. File names that end with
      '.zsav' are compressed using the ZLIB (ZSAV) compression scheme
      (requires v21 SPSS I/O files), while for file names that end with '.sav'
      the 'old' compression scheme is used (it is not possible to generate
      uncompressed files unless you modify the source code).
    -varNames: list of the variable names in the order in which they appear in
      in the spss data file.
    -varTypes: varTypes dictionary {varName: varType}, where varType == 0 means
      'numeric', and varType > 0 means 'character' of that length (in bytes)

    * Optional (the associated SPSS commands are given in CAPS)
    -valueLabels: value label dictionary {varName: {value: label}} Cf. VALUE
      LABELS (default: None)
    -varLabels: variable label dictionary {varName: varLabel}. Cf. VARIABLE
      LABEL (default: None)
    -formats: format_ dictionary {varName: printFmt} Cf. FORMATS
      (default: None)
    -missingValues: missing values dictionary {varName: {missing value spec}}
      (default: None). Cf. MISSING VALUES. For example:
          {'someNumvar1': {'values': [999, -1, -2]}, # discrete values
           'someNumvar2': {'lower': -9, 'upper':-1}, # range, cf. -9 THRU -1
           'someNumvar3': {'lower': -9, 'upper':-1, 'value': 999},
           'someStrvar1': {'values': ['foo', 'bar', 'baz']},
           'someStrvar2': {'values': 'bletch'}}
    ---The following three parameters must all three be set, if used---
    -measureLevels: measurement level dictionary {varName: <level>}
     Valid levels are: "unknown", "nominal", "ordinal", "scale",
     "ratio", "flag", "typeless". Cf. VARIABLE LEVEL (default: None)
    -columnWidths: column display width dictionary {varName: <int>}.
      Cf. VARIABLE WIDTH. (default: None --> >= 10 [stringVars] or automatic
      [numVars])
    -alignments: alignment dictionary {varName: <left/center/right>}
      Cf. VARIABLE ALIGNMENT (default: None --> left)
    ---
    -varSets: sets dictionary {setName: list_of_valid_varNames}.
      Cf. SETSMR command. (default: None)
    -varRoles: variable roles dictionary {varName: varRole}, where varRole
      may be any of the following: 'both', 'frequency', 'input', 'none',
      'partition', 'record ID', 'split', 'target'. Cf. VARIABLE ROLE
      (default: None)
    -varAttributes: variable attributes dictionary {varName: {attribName:
      attribValue} (default: None). For example: varAttributes = {'gender':
      {'Binary': 'Yes'}, 'educ': {'DemographicVars': '1'}}. Cf. VARIABLE
      ATTRIBUTES. (default: None)
    -fileAttributes: file attributes dictionary {attribName: attribValue}
      For example: {'RevisionDate[1]': '10/29/2004', 'RevisionDate[2]':
      '10/21/2005'}. Square brackets indicate attribute arrays, which must
      start with 1. Cf. FILE ATTRIBUTES. (default: None)
    -fileLabel: file label string, which defaults to "File created by user
      <username> at <datetime>" is file label is None. Cf. FILE LABEL
      (default: None)
    -multRespDefs: Multiple response sets definitions (dichotomy groups or
      category groups) dictionary {setName: <set definition>}. In SPSS syntax,
      'setName' has a dollar prefix ('$someSet'). See also docstring of
      multRespDefs method. Cf. MRSETS. (default: None)

    -caseWeightVar: valid varName that is set as case weight (cf. WEIGHT BY)
    -overwrite: Boolean that indicates whether an existing Spss file should be
      overwritten (default: True)
    -ioUtf8: indicates the mode in which text communicated to or from the
      I/O Module will be. Valid values are True (UTF-8/unicode mode, cf. SET
      UNICODE=ON) or False (Codepage mode, SET UNICODE=OFF) (default: False)
    -ioLocale: indicates the locale of the I/O module, cf. SET LOCALE (default:
      None, which is the same as locale.getlocale()[0])
    -mode: indicates the mode in which <savFileName> should be opened. Possible
      values are "wb" (write), "ab" (append), "cp" (copy: initialize header
      using <refSavFileName> as a reference file, cf. APPLY DICTIONARY).
      (default: "wb")
    -refSavFileName: reference file that should be used to initialize the
      header (aka the SPSS data dictionary) containing variable label, value
      label, missing value, etc etc definitions. Only relevant in conjunction
      with mode="cp". (default: None)

    Typical use:
    records = [['Test1', 1, 1], ['Test2', 2, 1]]
    varNames = ['var1', 'v2', 'v3']
    varTypes = {'var1': 5, 'v2': 0, 'v3': 0}
    savFileName = "test.sav"
    with SavWriter(savFileName, varNames, varTypes) as sav:
        sav.writerows(records)
    """
    def __init__(self, savFileName, varNames, varTypes, valueLabels=None,
                 varLabels=None, formats=None, missingValues=None,
                 measureLevels=None, columnWidths=None, alignments=None,
                 varSets=None, varRoles=None, varAttributes=None,
                 fileAttributes=None, fileLabel=None, multRespDefs=None,
                 caseWeightVar=None, overwrite=True, ioUtf8=False, 
                 ioLocale=None, mode="wb", refSavFileName=None):
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
        #self._getVarHandles()

        if self.mode == "wb":
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
        if self.mode in ("wb", "cp"):
            self._commitHeader()
        self.caseBuffer = self.getCaseBuffer()

    def __enter__(self):
        """This function returns the writer object itself so the writerow and
        writerows methods become available for use with 'with' statements"""
        return self

    def __exit__(self, type, value, tb):
        """ This function closes the spss data file."""
        if type is not None:
            pass  # Exception occurred
        self.closeSavFile(self.fh, mode="wb")

    def _getVarHandles(self):
        """This function returns a handle for a variable, which can then be
        used to read or write (depending on how the file was opened) values
        of the variable. If handle is associated with an output file, the
        dictionary must be written with spssCommitHeader before variable
        handles can be obtained via spssGetVarHandle. Helper function for
        __setitem__. *Not currently used*"""
        varHandles = {}
        varHandle = c_double()
        func = self.spssio.spssGetVarHandle
        for varName in self.varNames:
            retcode = func(c_int(self.fh), c_char_p(varName), byref(varHandle))
            varHandles[varName] = varHandle.value
            if retcode > 0:
                msg = "Error getting variable handle for variable %r"
                raise SPSSIOError(msg % varName, retcode)
        return varHandles

    def __setitem__(self, varName, value):
        """This function sets the value of a variable for the current case.
        The current case is not written out to the data file until
        spssCommitCaseRecord is called. *Not currently used*, but it was just
        begging to be implemented. ;-) Do NOT use in conjunction with
        wholeCaseOut. For example: self['someNumVar'] = 10
                                   self['someStrVar'] = 'foo'"""
        if not isinstance(value, (float, int, basestring)):
            raise ValueError("Value %r has wrong type: %s" %
                             value, type(value))
        varHandle = self.varHandles[varName]
        if self.varTypes[varName] == 0:
            funcN = self.spssio.spssSetValueNumeric
            retcode = funcN(c_int(self.fh), c_double(varHandle),
                            c_double(value))
        else:
            funcC = self.spssio.spssSetValueChar
            retcode = funcC(c_int(self.fh), c_double(varHandle),
                            c_char_p(value))
        if retcode > 0:
            isString = isinstance(value, basestring)
            valType = "character" if isString else "numerical"
            msg = "Error setting %s value %r for variable %r"
            raise SPSSIOError(msg % (valType, value, varName), retcode)

    def _openWrite(self, savFileName, overwrite):
        """ This function opens a file in preparation for creating a new IBM
        SPSS Statistics data file"""
        if os.path.exists(savFileName) and not os.access(savFileName, os.W_OK):
            raise IOError("No write access for file %r" % savFileName)

        if overwrite or not os.path.exists(savFileName):
            # always compress files, either zsav or standard.
            if savFileName.lower().endswith(".zsav"):
                self.fileCompression = "zlib"  # only with v21 libraries!
            else:
                self.fileCompression = "standard"
        elif not overwrite and os.path.exists(savFileName):
            raise IOError("File %r already exists!" % savFileName)

    def convertDate(self, day, month, year):
        """This function converts a Gregorian date expressed as day-month-year
        to the internal SPSS date format. The time portion of the date variable
        is set to 0:00. To set the time portion if the date variable to another
        value, use convertTime."""
        d, m, y = c_int(day), c_int(month), c_int(year)
        spssDate = c_double()
        retcode = self.spssio.spssConvertDate(d, m, y, byref(spssDate))
        if retcode > 0:
            msg = "Problem converting date value '%s-%s-%s'" % (d, m, y)
            raise SPSSIOError(msg, retcode)
        return spssDate.value

    def convertTime(self, day, hour, minute, second):
        """This function converts a time given as day, hours, minutes, and
        seconds to the internal SPSS time format."""
        d, h, m, s, spssTime = (c_int(day), c_int(hour), c_int(minute),
                                c_double(float(second)), c_double())
        retcode = self.spssio.spssConvertTime(d, h, m, s, byref(spssTime))
        if retcode > 0:
            msg = ("Problem converting time value '%s %s:%s:%s'" %
                  (day, hour, minute, second))
            raise SPSSIOError(msg, retcode)
        return spssTime.value

    def spssDateTime(self, datetimeStr="2001-12-08", strptimeFmt="%Y-%m-%d"):
        """ This function converts a date/time string into an SPSS date,
        using a strptime format."""
        dt = time.strptime(datetimeStr, strptimeFmt)
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
        if retcode > 0:
            raise SPSSIOError("Problem committing header", retcode)

    def _getPaddingLookupTable(self, varTypes):
        """Helper function that returns a lookup table that maps string lengths
        to string lengths to the nearest ceiled multiple of 8. For example:
        {1:%-8s, 7:%-8s, 9: %-16s, 24: %-24s}. Purpose: Get rid of trailing
        null bytes"""
        strLengths = varTypes.values()
        return dict([(i, "%%-%ds" % (-8 * (i // -8))) for i in strLengths])

    def writerow(self, record):
        if cWriterowOK:
            cWriterow(self, record)
            return
        self._pyWriterow(record)

    def _pyWriterow(self, record):
        """ This function writes one record, which is a Python list."""
        float_ = float
        for i, value in enumerate(record):
            varName = self.varNames[i]
            varType = self.varTypes[varName]
            if varType == 0:
                try:
                    value = float_(value)
                except ValueError:
                    value = self.sysmis_
                except TypeError:
                    value = self.sysmis_                    
            else:
                # Get rid of trailing null bytes --> 7 x faster than 'ljust'
                value = self.pad_8_lookup[varType] % value
                if self.ioUtf8_:
                    if isinstance(value, unicode):
                        value = value.encode("utf-8")
            record[i] = value
        self.record = record

    def writerows(self, records):
        """ This function writes all records."""
        nCases = len(records)
        for case, record in enumerate(records):
            self.writerow(record)
            self.printPctProgress(case, nCases)
