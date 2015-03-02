#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Read a file containg all the supported date formats
##############################################################################

import nose
import os
import tempfile
import sys
import functools
import locale
from time import strftime, strptime
from savReaderWriter import *

if sys.version_info[0] > 2:
    bytes = functools.partial(bytes, encoding='utf-8')

locale.setlocale(locale.LC_ALL, "")


# ----------------
# make sure the test passes in other locales too
stamp  = lambda v, fmt: bytes(strftime(fmt, strptime(v, '%Y-%m-%d')))
wed1, august = stamp('2010-08-11', '%A'), stamp('2010-08-11', '%B')
wed2, january = stamp('1910-01-12', '%A'), stamp('1910-01-12', '%B')
desired_records = \
    [[b'2010-08-11 00:00:00', b'32 WK 2010', b'2010-08-11', b'3 Q 2010',
      b'2010-08-11', b'2010-08-11', b'156260 00:00:00', b'2010-08-11', august,
      august + b' 2010', b'00:00:00.000000', b'2010-08-11', wed1],
     [b'1910-01-12 00:00:00', b'02 WK 1910', b'1910-01-12', b'1 Q 1910',
      b'1910-01-12', b'1910-01-12', b'119524 00:00:00', b'1910-01-12', january,
      january + b' 1910', b'00:00:00.000000', b'1910-01-12', wed2],
     [None, None, None, None, None, None, None,
      None, None, None, None, None, None],
     [None, None, None, None, None, None, None,
      None, None, None, None, None, None]]


# ----------------
# NOTE: PSPP does not know how to display all of these formats.
# Example use of DTIME in SPSS:
# COMPUTE #a_day = 24 * 60 * 60.
# COMPUTE x = 10 * #a_day + TIME.HMS(12, 03, 00).
# FORMATS x (DTIME14).
# will display as 10 12:03:00

savFileName = os.path.join(tempfile.gettempdir(), "test_dates.sav")

def setUp():
    """create a test file"""
    varNames = [b'var_datetime', b'var_wkyr', b'var_date', b'var_qyr', b'var_edate',
                b'var_sdate', b'var_dtime', b'var_jdate', b'var_month', b'var_moyr',
                b'var_time', b'var_adate', b'var_wkday']
    varTypes = {v : 0 for v in varNames}
    spssfmts = [b'DATETIME40', b'WKYR10', b'DATE10', b'QYR10', b'EDATE10',
                b'SDATE10', b'DTIME10', b'JDATE10', b'MONTH10', b'MOYR10',
                b'TIME10', b'ADATE10', b'WKDAY10']
    formats = dict(zip(varNames, spssfmts))
    records = [[b'2010-08-11' for v in varNames],
               [b'1910-01-12' for v in varNames],
               [b'' for v in varNames],
               [None for v in varNames]]

    kwargs = dict(savFileName=savFileName, varNames=varNames,
                  varTypes=varTypes, formats=formats)
    with SavWriter(**kwargs) as writer:
        for i, record in enumerate(records):
            for pos, value in enumerate(record):
                record[pos] = writer.spssDateTime(record[pos], "%Y-%m-%d")
            writer.writerow(record)

def tearDown():
    try:
        os.remove(savFileName)
    except:
        pass


# ----------------
@nose.with_setup(setUp)  #, tearDown)
def test_date_values():
    data = SavReader(savFileName)
    with data:
        actual_records = data.all()
    for desired_record, actual_record in zip(desired_records, actual_records):
        for desired, actual in zip(desired_record, actual_record):
            yield compare_value, desired, actual

@nose.with_setup(setUp, tearDown)
def test_dates_recodeSysmisTo():
    """Test if recodeSysmisTo arg recodes missing date value"""
    data = SavReader(savFileName, recodeSysmisTo=999)
    with data:
        actual_records = data.all()
    desired_records_ = desired_records[:2] + 2 * [13 * [999]]
    for desired_record, actual_record in zip(desired_records_, actual_records):
        for desired, actual in zip(desired_record, actual_record):
            yield compare_value, desired, actual

def compare_value(desired, actual):
    assert desired == actual


if __name__ == "__main__":
    nose.main()

