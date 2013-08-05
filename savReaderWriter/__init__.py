#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SavReaderWriter.py: A cross-platform Python interface to the IBM SPSS
Statistics Input Output Module. Read or Write SPSS system files (.sav, .zsav)

.. moduleauthor:: Albert-Jan Roskam <fomcl@yahoo.com>

"""

# change this to 'True' in case you experience segmentation
# faults related to freeing memory.
segfaults = False

import os

try:
    import psyco
    psycoOk = True  # reading 66 % faster
except ImportError:
    print ("NOTE. Psyco module not found. Install this module " +
           "to increase reader performance")
    psycoOk = False
try:
    import numpy
    numpyOk = True
except ImportError:
    print ("NOTE. Numpy module not found. Install this module " +
           "to use array slicing")
    numpyOk = False
try:
    from cWriterow import cWriterow  # writing 66 % faster
    cWriterowOK = True
except ImportError:
    print ("NOTE. cWriterow module not found. Install this module " +
            "to increase writer performance")
    cWriterowOK = False

__author__ = "Albert-Jan Roskam" + " " + "@".join(["fomcl", "yahoo.com"])
__version__ = open(os.path.join(os.path.dirname(__file__),
                                "VERSION")).read().strip()


allFormats = {
    1: ("SPSS_FMT_A", "Alphanumeric"),
    2: ("SPSS_FMT_AHEX", "Alphanumeric hexadecimal"),
    3: ("SPSS_FMT_COMMA", "F Format with commas"),
    4: ("SPSS_FMT_DOLLAR", "Commas and floating dollar sign"),
    5: ("SPSS_FMT_F", "Default Numeric Format"),
    6: ("SPSS_FMT_IB", "Integer binary"),
    7: ("SPSS_FMT_PIBHEX", "Positive integer binary - hex"),
    8: ("SPSS_FMT_P", "Packed decimal"),
    9: ("SPSS_FMT_PIB", "Positive integer binary unsigned"),
    10: ("SPSS_FMT_PK", "Positive integer binary unsigned"),
    11: ("SPSS_FMT_RB", "Floating point binary"),
    12: ("SPSS_FMT_RBHEX", "Floating point binary hex"),
    15: ("SPSS_FMT_Z", "Zoned decimal"),
    16: ("SPSS_FMT_N", "N Format- unsigned with leading 0s"),
    17: ("SPSS_FMT_E", "E Format- with explicit power of 10"),
    20: ("SPSS_FMT_DATE", "Date format dd-mmm-yyyy"),
    21: ("SPSS_FMT_TIME", "Time format hh:mm:ss.s"),
    22: ("SPSS_FMT_DATETIME", "Date and Time"),
    23: ("SPSS_FMT_ADATE", "Date format dd-mmm-yyyy"),
    24: ("SPSS_FMT_JDATE", "Julian date - yyyyddd"),
    25: ("SPSS_FMT_DTIME", "Date-time dd hh:mm:ss.s"),
    26: ("SPSS_FMT_WKDAY", "Day of the week"),
    27: ("SPSS_FMT_MONTH", "Month"),
    28: ("SPSS_FMT_MOYR", "mmm yyyy"),
    29: ("SPSS_FMT_QYR", "q Q yyyy"),
    30: ("SPSS_FMT_WKYR", "ww WK yyyy"),
    31: ("SPSS_FMT_PCT", "Percent - F followed by %"),
    32: ("SPSS_FMT_DOT", "Like COMMA, switching dot for comma"),
    33: ("SPSS_FMT_CCA", "User Programmable currency format"),
    34: ("SPSS_FMT_CCB", "User Programmable currency format"),
    35: ("SPSS_FMT_CCC", "User Programmable currency format"),
    36: ("SPSS_FMT_CCD", "User Programmable currency format"),
    37: ("SPSS_FMT_CCE", "User Programmable currency format"),
    38: ("SPSS_FMT_EDATE", "Date in dd/mm/yyyy style"),
    39: ("SPSS_FMT_SDATE", "Date in yyyy/mm/dd style")}

MAXLENGTHS = {
    "SPSS_MAX_VARNAME": (64, "Variable name"),
    "SPSS_MAX_SHORTVARNAME": (8, "Short (compatibility) variable name"),
    "SPSS_MAX_SHORTSTRING": (8, "Short string variable"),
    "SPSS_MAX_IDSTRING": (64, "File label string"),
    "SPSS_MAX_LONGSTRING": (32767, "Long string variable"),
    "SPSS_MAX_VALLABEL": (120, "Value label"),
    "SPSS_MAX_VARLABEL": (256, "Variable label"),
    "SPSS_MAX_7SUBTYPE": (40, "Maximum record 7 subtype"),
    "SPSS_MAX_ENCODING": (64, "Maximum encoding text")}

supportedDates = {  # uses ISO dates wherever applicable.
    "DATE": "%Y-%m-%d",
    "JDATE": "%Y-%m-%d",
    "EDATE": "%Y-%m-%d",
    "SDATE": "%Y-%m-%d",
    "DATETIME": "%Y-%m-%d %H:%M:%S",
    "ADATE": "%Y-%m-%d",
    "WKDAY": "%A",
    "MONTH": "%B",
    "MOYR": "%B %Y",
    "WKYR": "%W WK %Y",
    "QYR": "%m Q %Y",  # %m (month) is converted to quarter, see next dict.
    "TIME": "%H:%M:%S.%f",
    "DTIME": "%d %H:%M:%S"}

QUARTERS = {'01': '1', '02': '1', '03': '1', '04': '2', '05': '2', '06': '2',
            '07': '3', '08': '3', '09': '3', '10': '4', '11': '4', '12': '4'}

userMissingValues = {
    "SPSS_NO_MISSVAL": 0,
    "SPSS_ONE_MISSVAL": 1,
    "SPSS_TWO_MISSVAL": 2,
    "SPSS_THREE_MISSVAL": 3,
    "SPSS_MISS_RANGE": -2,
    "SPSS_MISS_RANGEANDVAL": -3}

version = __version__

from error import *
from generic import *
from header import *
from savReader import *
from savWriter import *
from savHeaderReader import *

__all__ = ["SavReader", "SavWriter", "SavHeaderReader"]
