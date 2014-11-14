#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import savReaderWriter as rw

# see: http://stackoverflow.com/questions/26895002/python-module-savreaderwriter-causing-segmentation-fault
class test_SavWriter_throws_no_segfault(unittest.TestCase):

savFileName = os.path.join(tempfile.gettempdir(), "some_file.sav")
varNames = [b"a_string", b"a_numeric"]
varTypes = {b"a_string": 1, b"a_numeric": 0}
records = [[b"x", 1], [b"y", 777], [b"z", 10 ** 6]]

# Incorrect, but now raises ctypes.ArgumentError:
valueLabels = {b"a_numeric": {b"1": b"male", b"2": b"female"},
               b"a_string": {1: b"male", 2: b"female"}}

# Correct
#valueLabels = {b"a_numeric": {1: b"male", 2: b"female"},
#               b"a_string": {b"1": b"male", b"2": b"female"}}

kwargs = dict(savFileName=savFileName, varNames=varNames, 
              varTypes=varTypes, valueLabels=valueLabels)
with rw.SavWriter(**kwargs) as writer:
    writer.writerows(records)

# Check if the valueLabels look all 
with rw.SavHeaderReader(savFileName) as header:
    metadata = header.dataDictionary(True)
    pprint.pprint(metadata.valueLabels)

