#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import cProfile
import pstats
import inspect
import timeit
import time
import sys

import savReaderWriter as rw

"""
Some performance tests for reading and writing
"""

print("@@@@@@ using cWriterow", rw.cWriterowOK, "@@@@@@")
print("@@@@@@ SAVRW_USE_CWRITEROW setting:",
      repr(os.environ.get("SAVRW_USE_CWRITEROW")), "@@@@@@")


def write_test(savFileName, nrows, ncols):
    varNames = ['v_%s' % i for i in range(ncols)]
    record = [b'aaaaa', 0] * (int(ncols) // 2)
    cmd = "5 if i % 2 == 0 else 0"
    varTypes = {varName: eval(cmd) for i, varName in enumerate(varNames)}
    with rw.SavWriter(savFileName, varNames, varTypes) as writer:
        for i in range(nrows):
            writer.writerow(record)

def read_test(savFileName):
    with rw.SavReader(savFileName) as reader:
        for i, record in enumerate(reader):
            if i % 10 ** 6 == 0:
                print("record %s, %s" % (i, time.asctime()))



os.chdir((os.path.dirname(os.path.abspath(__file__))))
savFileName = "profile_test.sav"

if len(sys.argv) == 1:
    nrows = 1000000
    ncols = 100
    read = False
    snippet = False
    write = True
else:
    try:
        nrows, ncols, read, snippet, write = sys.argv[1:]
    except:
        print("nrows, ncols, read, snippet, write")


# ------------------- writing -------------------
if write:
    print("start writing: ", time.asctime())
    print("nrows: %s || ncols: %s" %(nrows, ncols))
    write_results = 'write_results'
    cProfile.run('write_test(savFileName, nrows, ncols)', write_results)
    p = pstats.Stats(write_results)
    p.sort_stats('cumulative').print_stats(25)
    print("stop writing: ", time.asctime())

if snippet:
    setup = ("import savReaderWriter as rw\n%s\n"
             "savFileName = '%s'; nrows = %d; ncols = %d\n")
    setup = setup % (inspect.getsource(write_test), savFileName, nrows, ncols)
    print(timeit.repeat('write_test(savFileName, nrows, ncols)',
                        setup=setup, repeat=3, number=20))


# ------------------- reading -------------------
if read:
    print("start reading: ", time.asctime())
    read_results = 'read_results'
    cProfile.run('read_test(savFileName)', read_results)
    p = pstats.Stats(read_results)
    p.sort_stats('cumulative').print_stats(25)
    print("stop reading: ", time.asctime())
    timeit.timeit('read_test(savFileName)')

#os.remove(savFileName)

