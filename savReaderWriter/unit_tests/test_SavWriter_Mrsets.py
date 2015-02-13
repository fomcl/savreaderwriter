#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
from savReaderWriter import SavWriter

records = [[1000, b"higher"], [2000, b"university"], 
           [2000, b"\xe5\xa4\xa7\xe5\xad\xa6 (chinese university)"]]

savFileName = os.path.join(tempfile.gettempdir(), "mrdefs_test.sav")
varNames = [b"income", b"educ"]
varTypes = {b"income": 0, b"educ": 30}

categorical =  {b"setType": b"C", 
                b"label": b"labelC",
                b"varNames": [b"salary", b"educ"]}
dichotomous1 = {b"setType": b"D", b"label": b"labelD",
                b"varNames": [b"salary", b"educ"], 
                b"countedValue": b"Yes"}
multRespDefs = {b"testSetC": categorical, 
                b"testSetD1": dichotomous1}
#multRespDefs = {b"testSetD1": dichotomous1}
#multRespDefs = {b"testSetC": categorical} 
with SavWriter(savFileName, varNames, varTypes, multRespDefs=multRespDefs) as writer:
    writer.writerows(records)

