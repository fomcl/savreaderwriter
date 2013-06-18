#!/usr/bin/env python
# -*- coding: utf-8 -*-

from savReaderWriter import *
from generic import *

__version__ = version

class Header(Generic):

    """
    This class contains methods responsible for getting and setting meta data
    that is embedded in the IBM SPSS Statistics data file. In SPSS speak, this
    header information is known as the SPSS Data Dictionary (which has diddly
    squat to do with a Python dictionary!).
    """

    def __init__(self, savFileName, mode, refSavFileName, ioUtf8, ioLocale=None):
        """Constructor"""
        super(Header, self).__init__(savFileName, ioUtf8, ioLocale)
        self.spssio = self.loadLibrary()
        self.libc = cdll.LoadLibrary(ctypes.util.find_library("c"))
        self.fh = super(Header, self).openSavFile(savFileName, mode,
                                                  refSavFileName)
        self.varNames, self.varTypes = self.varNamesTypes
        self.vNames = dict(zip(self.varNames, self.encode(self.varNames)))

    def openSavFile(self):
        """This function returns the file handle that was opened in the
        super class"""
        return self.fh

##    def decode(func):
##        """Decorator to Utf-8 decode all str items contained in a dictionary
##        If ioUtf8=True, the dictionary's keys and values are decoded, but only
##        values that are strs, lists, or dicts. For example:
##        {'v1': {'y': 'yy', 'z': 666}}-->{u'v1': {u'y': u'yy', u'z': 666}}"""
##        uS = lambda x: x.decode("utf-8") if isinstance(x, str) else x
##        uL = lambda x: map(uS, x) if isinstance(x, list) else x
##
##        @functools.wraps(func)
##        def wrapper(arg):
##            result = func(arg)
##            if not arg.ioUtf8:
##                return result  # unchanged
##            if isinstance(result, str):
##                return uS(result)
##            utf8ifiedDict = {}
##            for k, v in result.iteritems():
##                k, v = uS(k), uS(v)
##                if isinstance(v, list):
##                    v = map(uS, v)
##                elif isinstance(v, dict):
##                    v = dict([(uS(x), uL(uS(y))) for x, y in v.items()])
##                utf8ifiedDict[k] = v
##            return utf8ifiedDict
##        return wrapper

    def decode(func):
        """Decorator to Utf-8 decode all str items contained in a dictionary
        If ioUtf8=True, the dictionary's keys and values are decoded, but only
        values that are strs, lists, or dicts. For example:
        >>> @decode
        ... def test(d):
        ...     return d
        >>> # test 1
        >>> test({'v1': {'y': 'yy', 'z': 666}})
        {u'v1': {u'y': u'yy', u'z': 666}}
        >>> # test 2
        >>> thai = ('\xe0\xb8\xaa\xe0\xb8\xa7\xe0\xb8\xb1' +
        ...         '\xe0\xb8\xaa\xe0\xb8\x94\xe0\xb8\xb5')
        >>> d = {'dichotomous3': {'countedValue': thai,
        ...      'label': thai, 'setType': 'D', 'varNames': ['v1', 'v2']}}
        >>> uthai = thai.decode("utf-8")
        >>> test(d) == {u'dichotomous3': {u'countedValue': uthai,
        ...             u'label': uthai,
        ...             u'setType': u'D',
        ...             u'varNames': [u'v1', u'v2']}}
        True
        """
        uS = lambda x: x.decode("utf-8") if isinstance(x, str) else x
        uL = lambda x: map(uS, x) if isinstance(x, list) else x
        @functools.wraps(func)
        def wrapper(arg):
            result = func(arg)
            if not arg.ioUtf8:
                return result  # unchanged
            if isinstance(result, str):
                return uS(result)
            uresult = {}
            for k, v in result.iteritems():
                uresult[uS(k)] = {}
                try:
                    for i, j in v.iteritems():  # or wrapper(j) recursion?
                        uresult[uS(k)][uS(i)] = uS(uL(j))
                except AttributeError:
                    uresult[uS(k)] = uL(uS(v))
            return uresult
        return wrapper

    def encode(self, item):
        """Counter part of decode helper function, does the opposite of that
        function (but is not a decorator)"""
        if not self.ioUtf8:
            return item  # unchanged
        utf8dify = lambda x: x.encode("utf-8") if isinstance(x, unicode) else x
        if isinstance(item, list):
            return map(utf8dify, item)
        elif isinstance(item, dict):
            return dict([(utf8dify(x), utf8dify(y)) for x, y in item.items()])
        return utf8dify(item)

    def freeMemory(self, funcName, *args):
        """Clean up: free memory claimed by e.g. getValueLabels and
        getVarNamesTypes"""
        gc.collect()
        if segfaults:
            return
        #print ".. freeing" , funcName[8:]
        func = getattr(self.spssio, funcName)
        retcode = func(*args)
        if retcode > 0:
            msg = "Error freeing memory using %s" % funcName
            raise SPSSIOError(msg, retcode)

    @property
    def numberofCases(self):
        """This function reports the number of cases present in a data file.
        Prehistoric files (< SPSS v6.0) don't contain nCases info, therefore
        a guesstimate of the number of cases is given for those files"""
        nCases = c_long()
        func = self.spssio.spssGetNumberofCases
        retcode = func(c_int(self.fh), byref(nCases))
        if nCases.value == -1:
            func = self.spssio.spssGetEstimatedNofCases
            retcode = func(c_int(self.fh), byref(nCases))
        if retcode > 0:
            raise SPSSIOError("Error getting number of cases", retcode)
        return nCases.value

    @property
    def numberofVariables(self):
        """This function returns the number of variables (columns) in the
        spss dataset"""
        numVars = c_int()
        func = self.spssio.spssGetNumberofVariables
        retcode = func(c_int(self.fh), byref(numVars))
        if retcode > 0:
            raise SPSSIOError("Error getting number of variables", retcode)
        return numVars.value

    @property
    def varNamesTypes(self):
        """Get/Set variable names and types.
        --Variable names is a list of the form ['var1', var2', 'etc']
        --Variable types is a dictionary of the form {varName: varType}
        The variable type code is an integer in the range 0-32767, 0
        indicating a numeric variable (F8.2) and a positive value
        indicating a string variable of that size (in bytes)."""
        if hasattr(self, "varNames"):
            return self.varNames, self.varTypes

        # initialize arrays
        numVars = self.numberofVariables
        numVars_ = c_int(numVars)
        varNamesArr = (POINTER(c_char_p * numVars))()
        varTypesArr = (POINTER(c_int * numVars))()

        # get variable names
        func = self.spssio.spssGetVarNames
        retcode = func(c_int(self.fh), byref(numVars_),
                       byref(varNamesArr), byref(varTypesArr))
        if retcode > 0:
            raise SPSSIOError("Error getting variable names & types", retcode)

        # get array contents
        varNames = [varNamesArr[0][i] for i in xrange(numVars)]
        varTypes = [varTypesArr[0][i] for i in xrange(numVars)]
        if self.ioUtf8:
            varNames = [varName.decode("utf-8") for varName in varNames]

        # clean up
        args = (varNamesArr, varTypesArr, numVars)
        self.freeMemory("spssFreeVarNames", *args)

        return varNames, dict(zip(varNames, varTypes))

    @varNamesTypes.setter
    def varNamesTypes(self, varNamesVarTypes):
        badLengthMsg = "Empty or longer than %s chars" % \
                       (MAXLENGTHS['SPSS_MAX_VARNAME'][0])
        varNames, varTypes = varNamesVarTypes
        varNameRetcodes = {
            0: ('SPSS_NAME_OK', 'Valid standard name'),
            1: ('SPSS_NAME_SCRATCH', 'Valid scratch var name'),
            2: ('SPSS_NAME_SYSTEM' 'Valid system var name'),
            3: ('SPSS_NAME_BADLTH', badLengthMsg),
            4: ('SPSS_NAME_BADCHAR', 'Invalid character or embedded blank'),
            5: ('SPSS_NAME_RESERVED', 'Name is a reserved word'),
            6: ('SPSS_NAME_BADFIRST', 'Invalid initial char (otherwise OK)')}
        validate = self.spssio.spssValidateVarname
        func = self.spssio.spssSetVarName
        for varName in self.varNames:
            varLength = self.varTypes[varName]
            retcode = validate(c_char_p(varName))
            if retcode > 0:
                msg = "%r is an invalid variable name [%r]" % \
                      (varName, ": ".join(varNameRetcodes.get(retcode)))
                raise SPSSIOError(msg, retcode)
            retcode = func(c_int(self.fh), c_char_p(varName), c_int(varLength))
            if retcode > 0:
                msg = "Problem setting variable name %r" % varName
                raise SPSSIOError(msg, retcode)

    @property
    @decode
    def valueLabels(self):
        """Get/Set VALUE LABELS.
        Takes a dictionary of the form {varName: {value: valueLabel}:
        --{'numGender': {1: 'female', {2: 'male'}}
        --{'strGender': {'f': 'female', 'm': 'male'}}"""
        def initArrays(isNumeric=True, size=1000):
            """default size assumes never more than 1000 labels"""
            labelsArr = (POINTER(c_char_p * size))()
            if isNumeric:
                return (POINTER(c_double * size))(), labelsArr
            return (POINTER(c_char_p * size))(), labelsArr

        valueLabels = {}
        for varName in self.varNames:
            vName = self.vNames[varName]
            numLabels = c_int()

            # step 1: get array size (numeric values)
            if self.varTypes[varName] == 0:
                valuesArr, labelsArr = initArrays(True)
                func = self.spssio.spssGetVarNValueLabels
                retcode = func(c_int(self.fh), c_char_p(vName),
                               byref(valuesArr), byref(labelsArr),
                               byref(numLabels))
                valuesArr, labelsArr = initArrays(True, numLabels.value)

            # step 1: get array size (string values)
            else:
                valuesArr, labelsArr = initArrays(False)
                func = self.spssio.spssGetVarCValueLabels
                retcode = func(c_int(self.fh), c_char_p(vName),
                               byref(valuesArr), byref(labelsArr),
                               byref(numLabels))
                valuesArr, labelsArr = initArrays(False, numLabels.value)

            # step 2: get labels with array of proper size
            retcode = func(c_int(self.fh), c_char_p(vName), byref(valuesArr),
                           byref(labelsArr), byref(numLabels))
            if retcode > 0:
                msg = "Error getting value labels of variable %r"
                raise SPSSIOError(msg % varName, retcode)

            # get array contents
            if not numLabels.value:
                continue
            values = [valuesArr[0][i] for i in xrange(numLabels.value)]
            labels = [labelsArr[0][i] for i in xrange(numLabels.value)]
            valueLabelsX = [(val, lbl) for val, lbl in zip(values, labels)]
            valueLabels[varName] = dict(valueLabelsX)

            # clean up
            args = (valuesArr, labelsArr, numLabels)
            if self.varTypes[varName] == 0:
                self.freeMemory("spssFreeVarNValueLabels", *args)
            else:
                self.freeMemory("spssFreeVarCValueLabels", *args)

        return valueLabels

    @valueLabels.setter
    def valueLabels(self, valueLabels):
        if not valueLabels:
            return
        valLabN = self.spssio.spssSetVarNValueLabel
        valLabC = self.spssio.spssSetVarCValueLabel
        valueLabels = self.encode(valueLabels)
        for varName, valueLabelsX in valueLabels.iteritems():
            valueLabelsX = self.encode(valueLabelsX)
            for value, label in valueLabelsX.iteritems():
                if self.varTypes[varName] == 0:
                    retcode = valLabN(c_int(self.fh), c_char_p(varName),
                                      c_double(value), c_char_p(label))
                else:
                    retcode = valLabC(c_int(self.fh), c_char_p(varName),
                                      c_char_p(value), c_char_p(label))
                if retcode > 0:
                    msg = "Problem with setting value labels of variable %r"
                    raise SPSSIOError(msg % varName, retcode)

    @property
    @decode
    def varLabels(self):
        """Get/set VARIABLE LABELS.
        Returns/takes a dictionary of the form {varName: varLabel}.
        For example: varLabels = {'salary': 'Salary (dollars)',
                                  'educ': 'Educational level (years)'}"""
        SPSS_VARLABEL_SHORT = 120  # fixed amount
        funcS = self.spssio.spssGetVarLabel
        funcL = self.spssio.spssGetVarLabelLong
        varLabels = {}
        for varName in self.varNames:
            varLabel = create_string_buffer(SPSS_VARLABEL_SHORT + 1)
            vName = self.vNames[varName]
            retcode = funcS(c_int(self.fh), c_char_p(vName), byref(varLabel))
            if varLabel.value and len(varLabel.value) > SPSS_VARLABEL_SHORT:
                lenBuff = MAXLENGTHS['SPSS_MAX_VARLABEL']
                varLabel = create_string_buffer(lenBuff)
                retcode = funcL(c_int(self.fh), c_char_p(varName),
                                byref(varLabel), c_int(lenBuff), byref(c_int))
            varLabels[varName] = varLabel.value
            if retcode > 0:
                msg = "Error getting variable label of variable %r" % varName
                raise SPSSIOError(msg, retcode)
        return varLabels

    @varLabels.setter
    def varLabels(self, varLabels):
        if not varLabels:
            return
        func = self.spssio.spssSetVarLabel
        varLabels = self.encode(varLabels)
        for varName, varLabel in varLabels.iteritems():
            retcode = func(c_int(self.fh), c_char_p(varName),
                           c_char_p(varLabel))
            if retcode > 0:
                msg = ("Problem with setting variable label %r of variable %r"
                       % (varLabel, varName))
                raise SPSSIOError(msg, retcode)

    @property
    @decode
    def formats(self):
        """Get the PRINT FORMATS, set PRINT and WRITE FORMATS.
        Returns/takes a dictionary of the form {varName: <format_>.
        For example: formats = {'salary': 'DOLLAR8', 'gender': 'A1',
                                'educ': 'F8.2'}"""
        if hasattr(self, "formats_"):
            return self.formats_
        printFormat_, printDec_, printWid_ = c_int(), c_int(), c_int()
        func = self.spssio.spssGetVarPrintFormat
        self.formats_ = {}
        for varName in self.varNames:
            vName = self.vNames[varName]
            retcode = func(c_int(self.fh), c_char_p(vName),
                           byref(printFormat_), byref(printDec_),
                           byref(printWid_))
            if retcode > 0:
                msg = "Error getting print format for variable %r"
                raise SPSSIOError(msg % vName, retcode)
            printFormat = allFormats.get(printFormat_.value)[0]
            printFormat = printFormat.split("_")[-1]
            format_ = printFormat + str(printWid_.value)
            if self.varTypes[varName] == 0:
                format_ += ("." + str(printDec_.value))
            if format_.endswith(".0"):
                format_ = format_[:-2]
            self.formats_[varName] = format_
        return self.formats_

    def _splitformats(self):
        """This function returns the 'bare' formats + variable widths,
        e.g. format_ F5.3 is returned as 'F' and '5'"""
        regex = re.compile("\w+(?P<varWid>\d+)[.]?\d?", re.I)
        bareformats, varWids = {}, {}
        for varName, format_ in self.formats.iteritems():
            bareformats[varName] = re.sub(r"\d+.", "", format_)
            varWids[varName] = int(regex.search(format_).group("varWid"))
        return bareformats, varWids

    @formats.setter
    def formats(self, formats):
        if not formats:
            return
        reverseFormats = dict([(v[0][9:], k) for k, v in allFormats.items()])
        validValues = sorted(reverseFormats.keys())
        regex = "(?P<printFormat>A(HEX)?)(?P<printWid>\d+)"
        isStringVar = re.compile(regex, re.IGNORECASE)
        regex = "(?P<printFormat>[A-Z]+)(?P<printWid>\d+)\.?(?P<printDec>\d*)"
        isAnyVar = re.compile(regex, re.IGNORECASE)
        funcP = self.spssio.spssSetVarPrintFormat  # print type
        funcW = self.spssio.spssSetVarWriteFormat  # write type
        for varName, format_ in self.encode(formats).iteritems():
            format_ = format_.upper()
            gotString = isStringVar.match(format_)
            gotAny = isAnyVar.match(format_)
            msg = ("Unknown format_ %r for variable %r. " +
                   "Valid formats are: %s")
            msg = msg % (", ".join(validValues), format_, varName)
            if gotString:
                printFormat = gotString.group("printFormat")
                printFormat = reverseFormats.get(printFormat)
                printDec = 0
                printWid = int(gotString.group("printWid"))
            elif gotAny:
                printFormat = gotAny.group("printFormat")
                printFormat = reverseFormats.get(printFormat)
                printDec = gotAny.group("printDec")
                printDec = int(printDec) if printDec else 0
                printWid = int(gotAny.group("printWid"))
            else:
                raise ValueError(msg)

            if printFormat is None:
                raise ValueError(msg)

            args = (c_int(self.fh), c_char_p(varName), c_int(printFormat),
                    c_int(printDec), c_int(printWid))
            retcode1, retcode2 = funcP(*args), funcW(*args)
            if retcodes.get(retcode1) == "SPSS_INVALID_PRFOR":
                # invalid PRint FORmat
                msg = "format_ for %r misspecified (%r)"
                raise SPSSIOError(msg % (varName, format_), retcode1)
            elif retcode1 > 0:
                msg = "Error setting format_ %r for %r"
                raise SPSSIOError(msg % (format_, varName), retcode1)

    def _getMissingValue(self, varName):
        """This is a helper function for the missingValues getter
        method.  The function returns the missing values of variable <varName>
        as a a dictionary. The dictionary keys and items depend on the
        particular definition, which may be discrete values and/or ranges.
        Range definitions are only possible for numerical variables."""
        if self.varTypes[varName] == 0:
            func = self.spssio.spssGetVarNMissingValues
            args = (c_double(), c_double(), c_double())
        else:
            func = self.spssio.spssGetVarCMissingValues
            args = (create_string_buffer(9), create_string_buffer(9),
                    create_string_buffer(9))
        missingFmt = c_int()
        vName = self.vNames[varName]
        retcode = func(c_int(self.fh), c_char_p(vName),
                       byref(missingFmt), *map(byref, args))
        if retcode > 0:
            msg = "Error getting missing value for variable %r"
            raise SPSSIOError(msg % varName, retcode)

        v1, v2, v3 = [v.value for v in args]
        userMiss = dict([(v, k) for k, v in userMissingValues.iteritems()])
        missingFmt = userMiss[missingFmt.value]
        if missingFmt == "SPSS_NO_MISSVAL":
            return {}
        elif missingFmt == "SPSS_ONE_MISSVAL":
            return {"values": [v1]}
        elif missingFmt == "SPSS_TWO_MISSVAL":
            return {"values": [v1, v2]}
        elif missingFmt == "SPSS_THREE_MISSVAL":
            return {"values": [v1, v2, v3]}
        elif missingFmt == "SPSS_MISS_RANGE":
            return {"lower": v1, "upper": v2}
        elif missingFmt == "SPSS_MISS_RANGEANDVAL":
            return {"lower": v1, "upper": v2, "value": v3}

    def _setMissingValue(self, varName, **kwargs):
        """This is a helper function for the missingValues setter
        method. The function sets missing values for variable <varName>.
        Valid keyword arguments are:
        * to specify a RANGE: 'lower', 'upper', optionally with 'value'
        * to specify DISCRETE VALUES: 'values', specified as a list no longer
        than three items, or as None, or as a float/int/str
        """
        if kwargs == {}:
            return 0
        fargs = ["lower", "upper", "value", "values"]
        if set(kwargs.keys()).difference(set(fargs)):
            raise ValueError("Allowed keywords are: %s" % ", ".join(fargs))
        varName = self.encode(varName)
        varType = self.varTypes[varName]

        # range of missing values, e.g. MISSING VALUES aNumVar (-9 THRU -1).
        if varType == 0:
            placeholder = 0.0
            if "lower" in kwargs and "upper" in kwargs and "value" in kwargs:
                missingFmt = "SPSS_MISS_RANGEANDVAL"
                args = kwargs["lower"], kwargs["upper"], kwargs["value"]
            elif "lower" in kwargs and "upper" in kwargs:
                missingFmt = "SPSS_MISS_RANGE"
                args = kwargs["lower"], kwargs["upper"], placeholder
        else:
            placeholder, args = "0", None

        # up to three discrete missing values
        if "values" in kwargs:
            values = self.encode(kwargs.values()[0])
            if isinstance(values, (float, int, str)):
                values = [values]

            # check if missing values strings values are not too long
            strMissLabels = [len(v) for v in values if isinstance(v, str)]
            if strMissLabels and max(strMissLabels) > 9:
                raise ValueError("Missing value label > 9 bytes")

            nvalues = len(values) if values is not None else values
            if values is None or values == {}:
                missingFmt = "SPSS_NO_MISSVAL"
                args = placeholder, placeholder, placeholder
            elif nvalues == 1:
                missingFmt = "SPSS_ONE_MISSVAL"
                args = values + [placeholder, placeholder]
            elif nvalues == 2:
                missingFmt = "SPSS_TWO_MISSVAL"
                args = values + [placeholder]
            elif nvalues == 3:
                missingFmt = "SPSS_THREE_MISSVAL"
                args = values
            else:
                msg = "You can specify up to three individual missing values"
                raise ValueError(msg)

        # numerical vars
        if varType == 0 and args:
            func = self.spssio.spssSetVarNMissingValues
            func.argtypes = [c_int, c_char_p, c_int,
                             c_double, c_double, c_double]
            args = map(float, args)
        # string vars
        else:
            if args is None:
                raise ValueError("Illegal keyword for character variable")
            func = self.spssio.spssSetVarCMissingValues
            func.argtypes = [c_int, c_char_p, c_int,
                             c_char_p, c_char_p, c_char_p]

        retcode = func(self.fh, varName, userMissingValues[missingFmt], *args)
        if retcode > 0:
            msg = "Problem setting missing value of variable %r"
            raise SPSSIOError(msg % varName, retcode)

    @property
    @decode
    def missingValues(self):
        """Get/Set MISSING VALUES.
        User missing values are values that will not be included in
        calculations by SPSS. For example, 'don't know' might be coded as a
        user missing value (a value of 999 is typically used, so when vairable
        'age' has values 5, 15, 999, the average age is 10). This is
        different from 'system missing values', which are blank/null values.
        Takes a dictionary of the following form:
          {'someNumvar1': {'values': [999, -1, -2]}, # discrete values
           'someNumvar2': {'lower': -9, 'upper':-1}, # range "-9 THRU -1"
           'someNumvar3': {'lower': -9, 'upper':-1, 'value': 999},
           'someStrvar1': {'values': ['foo', 'bar', 'baz']},
           'someStrvar2': {'values': 'bletch'}}      # shorthand """
        missingValues = {}
        for varName in self.varNames:
            missingValues[varName] = self._getMissingValue(varName)
        return missingValues

    @missingValues.setter
    def missingValues(self, missingValues):
        if missingValues:
            for varName, kwargs in missingValues.iteritems():
                self._setMissingValue(varName, **kwargs)

    # measurelevel, colwidth and alignment must all be set or not at all.
    @property
    @decode
    def measureLevels(self):
        """Get/Set VARIABLE LEVEL (measurement level).
        Returns/Takes a dictionary of the form {varName: varMeasureLevel}.
        Valid measurement levels are: "unknown", "nominal", "ordinal", "scale",
        "ratio", "flag", "typeless". This is used in Spss procedures such as
        CTABLES."""
        func = self.spssio.spssGetVarMeasureLevel
        levels = {0: "unknown", 1: "nominal", 2: "ordinal", 3: "scale",
                  3: "ratio", 4: "flag", 5: "typeless"}
        measureLevel = c_int()
        varMeasureLevels = {}
        for varName in self.varNames:
            vName = self.vNames[varName]
            retcode = func(c_int(self.fh), c_char_p(vName),
                           byref(measureLevel))
            varMeasureLevels[varName] = levels.get(measureLevel.value)
            if retcode > 0:
                msg = "Error getting variable measurement level: %r"
                raise SPSSIOError(msg % varName, retcode)

        return varMeasureLevels

    @measureLevels.setter
    def measureLevels(self, varMeasureLevels):
        if not varMeasureLevels:
            return
        func = self.spssio.spssSetVarMeasureLevel
        levels = {"unknown": 0, "nominal": 1, "ordinal": 2, "scale": 3,
                  "ratio": 3, "flag": 4, "typeless": 5}
        for varName, level in self.encode(varMeasureLevels).iteritems():
            if level.lower() not in levels:
                msg = "Valid levels are %"
                raise ValueError(msg % ", ".join(levels.keys()))
            level = levels.get(level.lower())
            retcode = func(c_int(self.fh), c_char_p(varName), c_int(level))
            if retcode > 0:
                msg = ("Error setting variable mesasurement level. " +
                       "Valid levels are: %s")
                raise SPSSIOError(msg % ", ".join(levels.keys()), retcode)

    @property
    @decode
    def columnWidths(self):
        """Get/Set VARIABLE WIDTH (display width).
        Returns/Takes a dictionary of the form {varName: <int>}. A value of
        zero is special and means that the IBM SPSS Statistics Data Editor
        is to set an appropriate width using its own algorithm. If used,
        variable alignment, measurement level and column width all needs to
        be set."""
        func = self.spssio.spssGetVarColumnWidth
        varColumnWidth = c_int()
        varColumnWidths = {}
        for varName in self.varNames:
            vName = self.vNames[varName]
            retcode = func(c_int(self.fh), c_char_p(vName),
                           byref(varColumnWidth))
            if retcode > 0:
                msg = ("Error getting column width: %r" % varName)
                raise SPSSIOError(msg, retcode)
            varColumnWidths[varName] = varColumnWidth.value
        return varColumnWidths

    @columnWidths.setter
    def columnWidths(self, varColumnWidths):
        if not varColumnWidths:
            return
        func = self.spssio.spssSetVarColumnWidth
        for varName, varColumnWidth in varColumnWidths.iteritems():
            retcode = func(c_int(self.fh), c_char_p(varName),
                           c_int(varColumnWidth))
            if retcode > 0:
                msg = "Error setting variable colunm width"
                raise SPSSIOError(msg, retcode)

    def _setColWidth10(self):
        """Set the variable display width of string values to at least 10
        (it's annoying that SPSS displays e.g. a one-character variable in
        very narrow columns). This also sets all measurement levels to
        "unknown" and all variable alignments to "left". This function is
        only called if column widths, measurement levels and variable
        alignments are None."""
        columnWidths = {}
        for varName, varType in self.varTypes.iteritems():
            # zero = appropriate width determined by spss
            columnWidths[varName] = 10 if 0 < varType < 10 else 0
        self.columnWidths = columnWidths
        self.measureLevels = dict([(v, "unknown") for v in self.varNames])
        self.alignments = dict([(v, "left") for v in self.varNames])

    @property
    @decode
    def alignments(self):
        """Get/Set VARIABLE ALIGNMENT.
        Returns/Takes a dictionary of the form {varName: alignment}
        Valid alignment values are: left, right, center. If used, variable
        alignment, measurement level and column width all need to be set.
        """
        func = self.spssio.spssGetVarAlignment
        alignments = {0: "left", 1: "right", 2: "center"}
        alignment_ = c_int()
        varAlignments = {}
        for varName in self.varNames:
            vName = self.vNames[varName]
            retcode = func(c_int(self.fh), c_char_p(vName),
                           byref(alignment_))
            alignment = alignments[alignment_.value]
            varAlignments[varName] = alignment
            if retcode > 0:
                msg = ("Error getting variable alignment: %r" % varName)
                raise SPSSIOError(msg, retcode)
        return varAlignments

    @alignments.setter
    def alignments(self, varAlignments):
        if not varAlignments:
            return
        func = self.spssio.spssSetVarAlignment
        alignments = {"left": 0, "right": 1, "center": 2}
        for varName, varAlignment in varAlignments.iteritems():
            if varAlignment.lower() not in alignments:
                msg = "Valid alignments are %"
                raise ValueError(msg % ", ".join(alignments.keys()))
            alignment = alignments.get(varAlignment.lower())
            retcode = func(c_int(self.fh), c_char_p(varName), c_int(alignment))
            if retcode > 0:
                msg = "Error setting variable alignment for variable %r"
                raise SPSSIOError(msg % varName, retcode)

    @property
    @decode
    def varSets(self):
        """Get/Set VARIABLE SET information.
        Returns/Takes a dictionary with SETNAME as keys and a list of SPSS
        variables as values. For example: {'SALARY': ['salbegin',
        'salary'], 'DEMOGR': ['gender', 'minority', 'educ']}"""
        varSets = c_char_p()
        func = self.spssio.spssGetVariableSets
        retcode = func(c_int(self.fh), byref(varSets))
        if retcode > 0:
            msg = "Problem getting variable set information"
            raise SPSSIOError(msg, retcode)
        if not varSets.value:
            return {}
        varSets_ = {}
        for varSet in varSets.value.split("\n")[:-1]:
            k, v = varSet.split("= ")
            varSets_[k] = v.split()

        # clean up
        self.freeMemory("spssFreeVariableSets", varSets)

        return varSets_

    @varSets.setter
    def varSets(self, varSets):
        if not varSets:
            return
        varSets_ = []
        for varName, varSet in varSets.iteritems():
            varSets_.append("%s= %s" % (varName, " ".join(varSet)))
        varSets_ = c_char_p("\n".join(varSets_))
        retcode = self.spssio.spssSetVariableSets(c_int(self.fh), varSets_)
        if retcode > 0:
            msg = "Problem setting variable set information"
            raise SPSSIOError(msg, retcode)

    @property
    @decode
    def varRoles(self):
        """Get/Set VARIABLE ROLES.
        Returns/Takes a dictionary of the form {varName: varRole}, where
        varRoles may be any of the following: 'both', 'frequency', 'input',
        'none', 'partition', 'record ID', 'split', 'target'"""
        func = self.spssio.spssGetVarRole
        roles = {0: "input", 1: "target", 2: "both", 3: "none", 4: "partition",
                 5: "split", 6: "frequency", 7: "record ID"}
        varRoles = {}
        varRole_ = c_int()
        for varName in self.varNames:
            vName = self.vNames[varName]
            retcode = func(c_int(self.fh), c_char_p(vName), byref(varRole_))
            varRole = roles.get(varRole_.value)
            varRoles[varName] = varRole
            if retcode > 0:
                msg = "Problem getting variable role for variable %r"
                raise SPSSIOError(msg % varName, retcode)
        return varRoles

    @varRoles.setter
    def varRoles(self, varRoles):
        if not varRoles:
            return
        roles = {"input": 0, "target": 1, "both": 2, "none": 3, "partition": 4,
                 "split": 5,  "frequency": 6, "record ID": 7}
        func = self.spssio.spssSetVarRole
        for varName, varRole in varRoles.iteritems():
            varRole = roles.get(varRole)
            retcode = func(c_int(self.fh), c_char_p(varName), c_int(varRole))
            if retcode > 0:
                msg = "Problem setting variable role %r for variable %r"
                raise SPSSIOError(msg % (varRole, varName), retcode)

    @property
    @decode
    def varAttributes(self):
        """Get/Set VARIABLE ATTRIBUTES.
        Returns/Takes dictionary of the form:
        {'var1': {'attr name x': 'attr value x','attr name y': 'attr value y'},
         'var2': {'attr name a': 'attr value a','attr name b': 'attr value b'}}
        """
        # abbreviation for readability and speed
        func = self.spssio.spssGetVarAttributes

        # initialize arrays
        MAX_ARRAY_SIZE = 1000
        attrNamesArr = (POINTER(c_char_p * MAX_ARRAY_SIZE))()
        attrValuesArr = (POINTER(c_char_p * MAX_ARRAY_SIZE))()

        attributes = {}
        for varName in self.varNames:
            vName = self.vNames[varName]

            # step 1: get array size
            nAttr = c_int()
            retcode = func(c_int(self.fh), c_char_p(vName),
                           byref(attrNamesArr), byref(attrValuesArr),
                           byref(nAttr))
            if retcode > 0:
                msg = "@Problem getting attributes of variable %r (step 1)"
                raise SPSSIOError(msg % varName, retcode)

            # step 2: get attributes with arrays of proper size
            nAttr = c_int(nAttr.value)
            attrNamesArr = (POINTER(c_char_p * nAttr.value))()
            attrValuesArr = (POINTER(c_char_p * nAttr.value))()
            retcode = func(c_int(self.fh), c_char_p(vName),
                           byref(attrNamesArr), byref(attrValuesArr),
                           byref(nAttr))
            if retcode > 0:
                msg = "Problem getting attributes of variable %r (step 2)"
                raise SPSSIOError(msg % varName, retcode)

            # get array contents
            if not nAttr.value:
                continue
            k, v, n = attrNamesArr[0], attrValuesArr[0], nAttr.value
            attribute = dict([(k[i], v[i]) for i in xrange(n)])
            attributes[varName] = attribute

            # clean up
            args = (attrNamesArr, attrValuesArr, nAttr)
            self.freeMemory("spssFreeAttributes", *args)

        return attributes

    @varAttributes.setter
    def varAttributes(self, varAttributes):
        if not varAttributes:
            return
        func = self.spssio.spssSetVarAttributes
        for varName in self.varNames:
            attributes = varAttributes.get(varName)
            if not attributes:
                continue
            nAttr = len(attributes)
            attrNames = (c_char_p * nAttr)(*attributes.keys())
            attrValues = (c_char_p * nAttr)(*attributes.values())
            retcode = func(c_int(self.fh), c_char_p(varName),
                           pointer(attrNames), pointer(attrValues),
                           c_int(nAttr))
            if retcode > 0:
                msg = "Problem setting variable attributes for variable %r"
                raise SPSSIOError(msg % varName, retcode)

    @property
    @decode
    def fileAttributes(self):
        """Get/Set DATAFILE ATTRIBUTES.
        Returns/Takes a dictionary of the form:
        {'attrName[1]': 'attrValue1', 'revision[1]': '2010-10-09',
        'revision[2]': '2010-10-22', 'revision[3]': '2010-11-19'}
         """
        # abbreviation for readability
        func = self.spssio.spssGetFileAttributes

        # step 1: get array size
        MAX_ARRAY_SIZE = 100  # assume never more than 100 file attributes
        attrNamesArr = (POINTER(c_char_p * MAX_ARRAY_SIZE))()
        attrValuesArr = (POINTER(c_char_p * MAX_ARRAY_SIZE))()
        nAttr = c_int()
        retcode = func(c_int(self.fh), byref(attrNamesArr),
                       byref(attrValuesArr), byref(nAttr))

        # step 2: get attributes with arrays of proper size
        nAttr = c_int(nAttr.value)
        attrNamesArr = (POINTER(c_char_p * nAttr.value))()
        attrValuesArr = (POINTER(c_char_p * nAttr.value))()
        retcode = func(c_int(self.fh), byref(attrNamesArr),
                       byref(attrValuesArr), byref(nAttr))
        if retcode > 0:
            raise SPSSIOError("Problem getting file attributes", retcode)

        # get array contents
        if not nAttr.value:
            return {}
        k, v = attrNamesArr[0], attrValuesArr[0]
        attributes = dict([(k[i], v[i]) for i in xrange(nAttr.value)])

        # clean up
        args = (attrNamesArr, attrValuesArr, nAttr)
        self.freeMemory("spssFreeAttributes", *args)

        return attributes

    @fileAttributes.setter
    def fileAttributes(self, fileAttributes):
        if not fileAttributes:
            return
        attributes, valueLens = {}, []
        for name, values in fileAttributes.iteritems():
            #valueLens.append(len(values))
            for value in values:
                attributes[name] = value
        nAttr = len(attributes)
        #nAttr = max(valueLens)  # n elements per vector. But this may vary??
        attrNames = (c_char_p * nAttr)(*attributes.keys())
        attrValues = (c_char_p * nAttr)(*attributes.values())
        func = self.spssio.spssSetFileAttributes
        retcode = func(c_int(self.fh), pointer(attrNames),
                       pointer(attrValues), c_int(nAttr))
        if retcode > 0:
            raise SPSSIOError("Problem setting file attributes", retcode)

    def _getMultRespDef(self, mrDef):
        """Get 'normal' multiple response defintions.
        This is a helper function for the multRespDefs getter function.
        A multiple response definition <mrDef> in the string format returned
        by the IO module is converted into a multiple response definition of
        the form multRespSet = {<setName>: {"setType": <setType>, "label":
        <lbl>, "varNames": <list_of_varNames>}}. SetType may be either 'D'
        (multiple dichotomy sets) or 'C' (multiple category sets). If setType
        is 'D', the multiple response definition also includes '"countedValue":
        countedValue'"""
        regex = "\$(?P<setName>\S+)=(?P<setType>[CD])\n?"
        m = re.search(regex + ".*", mrDef, re.I | re.U)
        if not m:
            return {}
        setType = m.group("setType")
        if setType == "C":  # multiple category sets
            regex += " (?P<lblLen>\d+) (?P<lblVarNames>.+) ?\n?"
            matches = re.findall(regex, mrDef, re.I)
            setName, setType, lblLen, lblVarNames = matches[0]
        else:               # multiple dichotomy sets
            # \w+ won't always work (e.g. thai) --> \S+
            regex += ("(?P<valueLen>\d+) (?P<countedValue>\S+)" +
                      " (?P<lblLen>\d+) (?P<lblVarNames>.+) ?\n?")
            matches = re.findall(regex, mrDef, re.I | re.U)
            setName, setType, valueLen = matches[0][:3]
            countedValue, lblLen, lblVarNames = matches[0][3:]
        lbl = lblVarNames[:int(lblLen)]
        varNames = lblVarNames[int(lblLen):].split()
        multRespSet = {setName: {"setType": setType, "label": lbl,
                                 "varNames": varNames}}
        if setType == "D":
            multRespSet[setName]["countedValue"] = countedValue
        return multRespSet

    def _setMultRespDefs(self, multRespDefs):
        """Set 'normal' multiple response defintions.
        This is a helper function for the multRespDefs setter function. 
        It translates the multiple response definition, specified as a
        dictionary, into a string that the IO module can use"""
        mrespDefs = []
        for setName, rest in multRespDefs.iteritems():
            rest = self.encode(rest)
            if rest["setType"] not in ("C", "D"):
                continue
            rest["setName"] = self.encode(setName)
            mrespDef = "$%(setName)s=%(setType)s" % rest
            lblLen = len(rest["label"])
            rest["lblLen"] = lblLen
            rest["varNames"] = " ".join(rest["varNames"])
            tail = " %(varNames)s" if lblLen == 0 else "%(label)s %(varNames)s"
            if rest["setType"] == "C":  # multiple category sets
                template = " %%(lblLen)s %s " % tail
            else:                       # multiple dichotomy sets
                # line below added/modified after Issue #4:
                # Assertion during creating of multRespDefs
                rest["valueLen"] = len(str(rest["countedValue"]))
                template = "%%(valueLen)s %%(countedValue)s %%(lblLen)s %s " \
                           % tail
            mrespDef += template % rest
            mrespDefs.append(mrespDef.rstrip())
        mrespDefs = "\n".join(mrespDefs)
        return mrespDefs

    def _getMultRespDefsEx(self, mrDef):
        """Get 'extended' multiple response defintions.
        This is a helper function for the multRespDefs getter function."""
        regex = ("\$(?P<setName>\w+)=(?P<setType>E) (?P<flag1>1)" +
                 "(?P<flag2>1)? (?P<valueLen>[0-9]+) (?P<countedValue>\w+) " +
                 "(?P<lblLen>[0-9]+) (?P<lblVarNames>[\w ]+)")
        matches = re.findall(regex, mrDef, re.I | re.U)
        setName, setType, flag1, flag2 = matches[0][:4]
        valueLen, countedValue, lblLen, lblVarNames = matches[0][4:]
        length = int(lblLen)
        label, varNames = lblVarNames[:length], lblVarNames[length:].split()
        return {setName: {"setType": setType, "firstVarIsLabel": bool(flag2),
                          "label": label, "countedValue": countedValue,
                          "varNames": varNames}}

    @property
    @decode
    def multRespDefs(self):
        """Get/Set MRSETS (multiple response) sets.
        Returns/takes a dictionary of the form:
        --multiple category sets: {setName: {"setType": "C", "label": lbl,
          "varNames": [<list_of_varNames>]}}
        --multiple dichotomy sets: {setName: {"setType": "D", "label": lbl,
          "varNames": [<list_of_varNames>], "countedValue": countedValue}}
        --extended multiple dichotomy sets: {setName: {"setType": "E",
          "label": lbl, "varNames": [<list_of_varNames>], "countedValue":
           countedValue, 'firstVarIsLabel': <bool>}}
	Note. You can get values of extended multiple dichotomy sets with 
        getMultRespSetsDefEx, but you cannot write extended multiple dichotomy
        sets.

        For example:
        categorical  = {"setType": "C", "label": "labelC",
                       "varNames": ["salary", "educ"]}
        dichotomous1 = {"setType": "D", "label": "labelD",
                        "varNames": ["salary", "educ"], "countedValue": "Yes"}
        dichotomous2 = {"setType": "D", "label": "", "varNames":
                        ["salary", "educ", "jobcat"], "countedValue": "No"}
        extended1    = {"setType": "E", "label": "", "varNames": ["mevar1",
                        "mevar2", "mevar3"], "countedValue": "1",
                        "firstVarIsLabel": True}
        extended2    = {"setType": "E", "label":
                        "Enhanced set with user specified label", "varNames":
                        ["mevar4", "mevar5", "mevar6"], "countedValue":
                        "Yes", "firstVarIsLabel": False}
        multRespDefs = {"testSetC": categorical, "testSetD1": dichotomous1,
                        "testSetD2": dichotomous2, "testSetEx1": extended1,
                        "testSetEx2": extended2}
        """
        #####
        # I am not sure whether 'extended' MR definitions complement
        # or replace 'normal' MR definitions. I assumed 'complement'.
        #####

        # Alternative approach
        #nSets = c_int()
        #func = self.spssio.spssGetMultRespCount
        #retcode = func(c_int(self.fh), byref(nSets))
        #if not nSets.value:
        #    return {}
        #func = self.spssio.spssGetMultRespDefByIndex
        #ppSet = c_char_p()
        #for i in range(nSets.value):
        #    retcode = func(c_int(self.fh), c_int(i), byref(ppSet))
        #    print ppSet.value, retcodes.get(retcode, retcode)
        #    if retcode > 0:
        #        msg = "Problem getting multiple response definitions"
        #        raise SPSSIOError(msg, retcode)
        #    self.freeMemory("spssFreeMultRespDefStruct", ppSet)

        ## Normal Multiple response definitions
        func = self.spssio.spssGetMultRespDefs
        mrDefs = c_char_p()
        retcode = func(c_int(self.fh), pointer(mrDefs))
        if retcode > 0:
            msg = "Problem getting multiple response definitions"
            raise SPSSIOError(msg, retcode)

        multRespDefs = {}
        if mrDefs.value:
            for mrDef in mrDefs.value.split("\n"):
                for setName, rest in self._getMultRespDef(mrDef).iteritems():
                    multRespDefs[setName] = rest
            self.freeMemory("spssFreeMultRespDefs", mrDefs)

        ## Extended Multiple response definitions
        mrDefsEx = c_char_p()
        func = self.spssio.spssGetMultRespDefsEx
        retcode = func(c_int(self.fh), pointer(mrDefsEx))
        if retcode > 0:
            msg = "Problem getting extended multiple response definitions"
            raise SPSSIOError(msg, retcode)

        multRespDefsEx = {}
        if mrDefsEx.value:
            for mrDefEx in mrDefsEx.value.split("\n"):
                for setName, rest in self._getMultRespDef(mrDefEx).iteritems():
                    multRespDefsEx[setName] = rest
            self.freeMemory("spssFreeMultRespDefs", mrDefsEx)

        multRespDefs.update(multRespDefsEx)
        return multRespDefs

    @multRespDefs.setter
    def multRespDefs(self, multRespDefs):
        if not multRespDefs:
            return
        multRespDefs = self._setMultRespDefs(multRespDefs)
        func = self.spssio.spssSetMultRespDefs
        retcode = func(c_int(self.fh), c_char_p(multRespDefs))
        if retcode > 0:
            msg = "Problem setting multiple response definitions"
            raise SPSSIOError(msg, retcode)

    @property
    @decode
    def caseWeightVar(self):
        """Get/Set WEIGHT variable.
        Takes a valid varName, and returns weight variable, if any, as a
        string."""
        varNameBuff = create_string_buffer(65)
        func = self.spssio.spssGetCaseWeightVar
        retcode = func(c_int(self.fh), byref(varNameBuff))
        if retcode > 0:
            msg = "Problem getting case weight variable name"
            raise SPSSIOError(msg, retcode)
        return varNameBuff.value

    @caseWeightVar.setter
    def caseWeightVar(self, varName):
        if not varName:
            return
        func = self.spssio.spssSetCaseWeightVar
        retcode = func(c_int(self.fh), c_char_p(varName))
        if retcode > 0:
            msg = "Problem setting case weight variable name %r" % varName
            raise SPSSIOError(msg, retcode)

    @property
    @decode
    def dateVariables(self):  # seems to be okay
        """Get/Set DATE information. This function reports the Forecasting
        (Trends) date variable information, if any, in IBM SPSS Statistics
        data files. Entirely untested and not implemented in reader/writer"""
        # step 1: get array size
        nElements = c_int()
        func = self.spssio.spssGetDateVariables
        MAX_ARRAY_SIZE = 100
        dateInfoArr = (POINTER(c_long * MAX_ARRAY_SIZE))()
        retcode = func(c_int(self.fh), byref(nElements), byref(dateInfoArr))

        # step 2: get date info with array of proper size
        dateInfoArr = (POINTER(c_long * nElements.value))()
        retcode = func(c_int(self.fh), byref(nElements), byref(dateInfoArr))
        if retcode > 0:
            raise SPSSIOError("Error getting TRENDS information", retcode)

        # get array contents
        nElem = nElements.value
        if not nElem:
            return {}
        dateInfo = [dateInfoArr[0][i] for i in xrange(nElem)]
        fixedDateInfo = dateInfo[:6]
        otherDateInfo = [dateInfo[i: i + 3] for i in xrange(6, nElem, 3)]
        dateInfo = {"fixedDateInfo": fixedDateInfo,
                    "otherDateInfo": otherDateInfo}

        # clean up
        self.freeMemory("spssFreeDateVariables", dateInfoArr)

        return dateInfo

    @dateVariables.setter
    def dateVariables(self, dateInfo):  # 'SPSS_INVALID_DATEINFO'!
        dateInfo = [dateInfo["fixedDateInfo"]] + dateInfo["otherDateInfo"]
        dateInfo = reduce(list.__add__, dateInfo)  # flatten list
        isAllInts = all([isinstance(d, int) for d in dateInfo])
        isSixPlusTriplets = (len(dateInfo) - 6) % 3 == 0
        if not isAllInts and isSixPlusTriplets:
            msg = ("TRENDS date info must consist of 6 fixed elements" +
                   "+ <nCases> three-element groups of other date info " +
                   "(all ints)")
            raise TypeError(msg)
        func = self.spssio.spssSetDateVariables
        nElements = len(dateInfo)
        dateInfoArr = (c_long * nElements)(*dateInfo)
        retcode = func(c_int(self.fh), c_int(nElements), dateInfoArr)
        if retcode > 0:
            raise SPSSIOError("Error setting TRENDS information", retcode)

    @property
    @decode
    def textInfo(self):
        """Get/Set text information.
        Takes a savFileName and returns a string of the form: "File %r built
        using SavReaderWriter.py version %s (%s)". This is akin to, but
        *not* equivalent to the SPSS syntax command DISPLAY DOCUMENTS"""
        textInfo = create_string_buffer(256)
        retcode = self.spssio.spssGetTextInfo(c_int(self.fh), byref(textInfo))
        if retcode > 0:
            raise SPSSIOError("Error getting textInfo", retcode)
        return textInfo.value

    @textInfo.setter
    def textInfo(self, savFileName):
        info = (os.path.basename(savFileName), __version__, time.asctime())
        textInfo = "File '%s' built using SavReaderWriter.py version %s (%s)"
        textInfo = textInfo % info
        if self.ioUtf8 and isinstance(savFileName, unicode):
            textInfo = textInfo.encode("utf-8")
        func = self.spssio.spssSetTextInfo
        retcode = func(c_int(self.fh), c_char_p(textInfo[:256]))
        if retcode > 0:
            raise SPSSIOError("Error setting textInfo", retcode)

    @property
    @decode
    def fileLabel(self):
        """Get/Set FILE LABEL (id string)
        Takes a file label (basestring), and returns file label, if any, as
        a string."""
        idStr = create_string_buffer(65)
        retcode = self.spssio.spssGetIdString(c_int(self.fh), byref(idStr))
        if retcode > 0:
            raise SPSSIOError("Error getting file label (id string)", retcode)
        return idStr.value

    @fileLabel.setter
    def fileLabel(self, idStr):
        if idStr is None:
            idStr = "File created by user %r at %s"[:64] % \
                    (getpass.getuser(), time.asctime())
        if self.ioUtf8 and isinstance(idStr, unicode):
            idStr = idStr.encode("utf-8")
        retcode = self.spssio.spssSetIdString(c_int(self.fh), c_char_p(idStr))
        if retcode > 0:
            raise SPSSIOError("Error setting file label (id string)", retcode)
