#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SavReaderWriter.py: A cross-platform Python interface to the IBM SPSS
Statistics Input Output Module. Read or Write SPSS system files (.sav, .zsav)

.. moduleauthor:: Albert-Jan Roskam <fomcl@yahoo.com>

"""

__author__ = "Albert-Jan Roskam" + " " + "@".join(["fomcl", "yahoo.com"])
__version__ = "3.1.1"

# change this to 'True' in case you experience segmentation
# faults related to freeing memory.
segfaults = False

from ctypes import *
import ctypes.util
import struct
import sys
import platform
import os
import re
import operator
import math
import locale
import datetime
import time
import getpass
import encodings
import functools
import gc
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

retcodes = {
    0: "SPSS_OK",
    1: "SPSS_FILE_OERROR",
    2: "SPSS_FILE_WERROR",
    3: "SPSS_FILE_RERROR",
    4: "SPSS_FITAB_FULL",
    5: "SPSS_INVALID_HANDLE",
    6: "SPSS_INVALID_FILE",
    7: "SPSS_NO_MEMORY",
    8: "SPSS_OPEN_RDMODE",
    9: "SPSS_OPEN_WRMODE",
    10: "SPSS_INVALID_VARNAME",
    11: "SPSS_DICT_EMPTY",
    12: "SPSS_VAR_NOTFOUND",
    13: "SPSS_DUP_VAR",
    14: "SPSS_NUME_EXP",
    15: "SPSS_STR_EXP",
    16: "SPSS_SHORTSTR_EXP",
    17: "SPSS_INVALID_VARTYPE",
    18: "SPSS_INVALID_MISSFOR",
    19: "SPSS_INVALID_COMPSW",
    20: "SPSS_INVALID_PRFOR",
    21: "SPSS_INVALID_WRFOR",
    22: "SPSS_INVALID_DATE",
    23: "SPSS_INVALID_TIME",
    24: "SPSS_NO_VARIABLES",
    27: "SPSS_DUP_VALUE",
    28: "SPSS_INVALID_CASEWGT",
    30: "SPSS_DICT_COMMIT",
    31: "SPSS_DICT_NOTCOMMIT",
    33: "SPSS_NO_TYPE2",
    41: "SPSS_NO_TYPE73",
    45: "SPSS_INVALID_DATEINFO",
    46: "SPSS_NO_TYPE999",
    47: "SPSS_EXC_STRVALUE",
    48: "SPSS_CANNOT_FREE",
    49: "SPSS_BUFFER_SHORT",
    50: "SPSS_INVALID_CASE",
    51: "SPSS_INTERNAL_VLABS",
    52: "SPSS_INCOMPAT_APPEND",
    53: "SPSS_INTERNAL_D_A",
    54: "SPSS_FILE_BADTEMP",
    55: "SPSS_DEW_NOFIRST",
    56: "SPSS_INVALID_MEASURELEVEL",
    57: "SPSS_INVALID_7SUBTYPE",
    58: "SPSS_INVALID_VARHANDLE",
    59: "SPSS_INVALID_ENCODING",
    60: "SPSS_FILES_OPEN",
    70: "SPSS_INVALID_MRSETDEF",
    71: "SPSS_INVALID_MRSETNAME",
    72: "SPSS_DUP_MRSETNAME",
    73: "SPSS_BAD_EXTENSION",
    74: "SPSS_INVALID_EXTENDEDSTRING",
    75: "SPSS_INVALID_ATTRNAME",
    76: "SPSS_INVALID_ATTRDEF",
    77: "SPSS_INVALID_MRSETINDEX",
    78: "SPSS_INVALID_VARSETDEF",
    79: "SPSS_INVALID_ROLE",

    -15: "SPSS_EMPTY_DEW",
    -14: "SPSS_NO_DEW",
    -13: "SPSS_EMPTY_MULTRESP",
    -12: "SPSS_NO_MULTRESP",
    -11: "SPSS_NO_DATEINFO",
    -10: "SPSS_NO_CASEWGT",
    -9: "SPSS_NO_LABEL",
    -8: "SPSS_NO_LABELS",
    -7: "SPSS_EMPTY_VARSETS",
    -6: "SPSS_NO_VARSETS",
    -5: "SPSS_FILE_END",
    -4: "SPSS_EXC_VALLABEL",
    -3: "SPSS_EXC_LEN120",
    -2: "SPSS_EXC_VARLABEL",
    -1: "SPSS_EXC_LEN64"}

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
    22: ("SPSS_FMT_DATE_TIME", "Date and Time"),
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
    "WKDAY": "%A %H:%M:%S",
    "ADATE": "%Y-%m-%d",
    "WKDAY": "%A",
    "MONTH": "%B",
    "MOYR": "%B %Y",
    "WKYR": "%W WK %Y"}

userMissingValues = {
    "SPSS_NO_MISSVAL": 0,
    "SPSS_ONE_MISSVAL": 1,
    "SPSS_TWO_MISSVAL": 2,
    "SPSS_THREE_MISSVAL": 3,
    "SPSS_MISS_RANGE": -2,
    "SPSS_MISS_RANGEANDVAL": -3}

version = __version__

from generic import *
from header import *
from savReader import *
from savWriter import *
from savHeaderReader import *
from error import *

__all__ = ["SavReader", "SavWriter", "SavHeaderReader"]
