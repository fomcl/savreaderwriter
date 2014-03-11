#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
## Write a file in utf8 mode aka unicode mode (ioUtf8=True)
##############################################################################

## ... check if non-ascii encodings work well
## ... notice the use of 'ioUtf8'
## ... source: http://www.omniglot.com/language/phrases/hello.htm

import unittest
import os
import tempfile
import copy
import sys
from savReaderWriter import *

greetings_expected = [
    [u'Arabic', u'\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u064a\u0643\u0645'],
    [u'Assamese', u'\u09a8\u09ae\u09b8\u09cd\u0995\u09be\u09f0'],
    [u'Bengali', u'\u0986\u09b8\u09b8\u09be\u09b2\u09be\u09ae\u09c1\u0986\u09b2\u09be\u0987\u0995\u09c1\u09ae'],
    [u'English', u'Greetings and salutations'],
    [u'Georgian', u'\u10d2\u10d0\u10db\u10d0\u10e0\u10ef\u10dd\u10d1\u10d0'],
    [u'Kazakh', u'\u0421\u04d9\u043b\u0435\u043c\u0435\u0442\u0441\u0456\u0437 \u0431\u0435'],
    [u'Russian', u'\u0417\u0434\u0440\u0430\u0432\u0441\u0442\u0432\u0443\u0439\u0442\u0435'],
    [u'Spanish', u'\xa1Hola!'],
    [u'Swiss German', u'Gr\xfcezi'],
    [u'Thai', u'\u0e2a\u0e27\u0e31\u0e2a\u0e14\u0e35'],
    [u'Walloon', u'Bondjo\xfb'],
    [u'Telugu', u'\u0c0f\u0c2e\u0c02\u0c21\u0c40']]

class test_SavWriter_ioUtf8(unittest.TestCase):
    """Write a file, ioUtf=True use"""

    def test_SavWriter_unicode_mode(self):

        savFileName = os.path.join(tempfile.gettempdir(), "test.sav")
        varNames = ["language", "greeting"]
        varTypes = {"language": 20, "greeting": 50}

        # this drove me insane (but only temporarily). Marvels of mutable data
        greetings_expected_loc = copy.deepcopy(greetings_expected)

        with SavWriter(savFileName, varNames, varTypes, ioUtf8=True) as writer:
            for greeting in greetings_expected_loc:
                greeting = [greet.encode("utf-8") for greet in greeting]
                writer.writerow(greeting)

        u = str if sys.version_info[0] > 2 else unicode
        with SavReader(savFileName, ioUtf8=True) as reader:
            greetings_got = []
            for record in reader:
                greetings_got.append(list(map(u.rstrip, record)))
        self.assertEqual(greetings_expected, greetings_got)

if __name__ == "__main__":
    unittest.main()
