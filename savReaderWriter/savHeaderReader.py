#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import collections
import locale

from savReaderWriter import *
from header import *

@implements_to_string
class SavHeaderReader(Header):
    """
    This class contains methods that read the data dictionary of an SPSS
    data file. This yields the same information as the Spss command `DISPLAY
    DICTIONARY`. NB: do not confuse an Spss dictionary with a Python
    dictionary!

    Parameters
    ----------
    savFileName : str
        The file name of the spss data file
    ioUtf8 : bool, optional
        Indicates the mode in which text communicated to or from 
        the I/O Module will be. Valid values are True (UTF-8 mode aka 
        Unicode mode) and False (Codepage mode). Cf. `SET UNICODE=ON/OFF`
    ioLocale : locale str, optional
        indicates the locale of the I/O module. Cf. `SET LOCALE`. 
        (default = None, which corresponds to 
        ``locale.setlocale(locale.LC_CTYPE)``)

    Examples
    --------

    Typical use::

        with SavHeaderReader(savFileName) as header:
            metadata = header.all()
            print(metadata.varLabels)
            print(str(header))
            report = header.reportSpssDataDictionary(header.all(False))

   See also
   --------
   savReaderWriter.Header : for more options to retrieve individual 
       metadata items"""

    def __init__(self, savFileName, ioUtf8=False, ioLocale=None):
        """ Constructor. Initializes all vars that can be recycled """
        super(SavHeaderReader, self).__init__(savFileName, b"rb", None,
                                              ioUtf8, ioLocale)
        self.fh = self.openSavFile()
        self.varNames, self.varTypes = self.varNamesTypes
        self.numVars = self.numberofVariables
        self.nCases = self.numberofCases

    def __str__(self):
        """ This function returns a report of the SPSS data dictionary
        (i.e., the header), in the encoding of the spss file"""
        return unicode(self).encode(self.fileEncoding)

    def __unicode__(self):
        """ This function returns a report of the SPSS data dictionary
        (i.e., the header)."""
        report = ""
        if self.textInfo:
            report += self.textInfo + os.linesep
        report += self.reportSpssDataDictionary(self.dataDictionary())
        return report

    def __enter__(self):
        """ This function returns the DictionaryReader object itself so
        its methods become available for use with context managers
        ('with' statements).

        .. warning::

            Always ensure the the .sav file is properly closed, either by 
            using a context manager (``with`` statement) or by using 
            ``close()``"""
        return self

    def __exit__(self, type, value, tb):
        """ This function closes the spss data file and does some cleaning."""
        if type is not None:
            pass  # Exception occurred
        self.close()

    def close(self):
        """This function closes the spss data file and does some cleaning."""
        if not segfaults:
            self.closeSavFile(self.fh, mode=b"rb")
        try:
            locale.resetlocale()  # fails on Windows
        except:
            locale.setlocale(locale.LC_ALL, "")

    def dataDictionary(self, asNamedtuple=False):
        """ This function returns all the dictionary items. It returns
        a Python dictionary based on the Spss dictionary of the given
        Spss file. This is equivalent to the Spss command 'DISPLAY
        DICTIONARY'. If asNamedtuple=True, this function returns a namedtuple,
        so one can retrieve metadata like e.g. 'metadata.valueLabels'"""
        items = ["varNames", "varTypes", "valueLabels", "varLabels",
                 "formats", "missingValues", "measureLevels",
                 "columnWidths", "alignments", "varSets", "varRoles",
                 "varAttributes", "fileAttributes", "fileLabel",
                 "multRespDefs", "caseWeightVar"] # "dateVariables"]
        if self.ioUtf8:
            items = map(unicode, items)
        metadata = dict([(item, getattr(self, item)) for item in items])
        if asNamedtuple:
            Meta = collections.namedtuple("Meta", " ".join(metadata.keys()))
            return Meta(*metadata.values())
        return metadata

    def all(self, asNamedtuple=True):
        """Returns all the metadata as a named tuple (cf. SavReader.all)
        Exactly the same as dataDictionary, but with different (nicer?)
        default"""
        return self.dataDictionary(asNamedtuple)

    def __getEntry(self, varName, k, v, enc):
        """Helper function for reportSpssDataDictionary"""
        try:
            k = k if self.ioUtf8 else k.decode(enc).strip()
        except AttributeError:
            pass
        try:
           v = list(v) if isinstance(v, map) else v
        except TypeError:
           pass  # python 2
        try:
            v =  v if self.ioUtf8 else v.decode(enc)
        except AttributeError:
            #v = ", ".join(map(str, v)) if isinstance(v, list) else v
            enc = self.fileEncoding
            func = lambda x: x.decode(enc) if isinstance(x, bytes) else str(x)
            v = ", ".join(map(func, v)) if isinstance(v, list) else v
        try:
            v = ", ".join(eval(str(v)))  # ??
        except:
            pass
        return "%s: %s -- %s" % (varName,k, v)

    def reportSpssDataDictionary(self, dataDict):
        """ This function reports information from the Spss dictionary
        of the active Spss dataset. The parameter 'dataDict' is the return
        value of dataDictionary()"""
        # Yeah I know: what a mess! ;-)
        report, enc = [], self.fileEncoding
        for kwd, allValues in sorted(dataDict.items()):
            report.append("#" + kwd.upper())
            if hasattr(allValues, "items"):
                for varName, values in sorted(allValues.items()):
                    varName =  varName if self.ioUtf8 else varName.decode(enc)
                    if hasattr(values, "items"):
                        for k, v in sorted(values.items()):
                            report.append(self.__getEntry(varName, k, v, enc))
                    else:
                        # varsets
                        if isinstance(values, list):
                            values = b", ".join(values)
                            entry = "%s -- %s" % (varName, values.decode(enc))
                            report.append(entry)
                        # variable role, label, level, format, colwidth, alignment, type
                        else:
                            try:
                                values =  values if self.ioUtf8 else values.decode(enc)
                            except AttributeError:
                                values = str(values)
                            report.append("%s -- %s" % (varName, values))
            else:
                # varname, file label
                if isinstance(allValues, (str, bytes, unicode)) and allValues:
                    allValues = [allValues]
                for varName in allValues:
                    if isinstance(varName, bytes):
                        varName = varName.decode(enc)
                    report.append(varName)
        return os.linesep.join(report)
