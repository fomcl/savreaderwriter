#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import tempfile
import locale

from savReaderWriter import *

# I had to generate a German locale with the (Windows) codepage 1252 on my
# Linux machine first
# http://documentation.basis.com/BASISHelp/WebHelp/inst/character_encoding.htm
# sudo localedef -f CP1252 -i de_DE /usr/lib/locale/de_DE.cp1252
# locale -a | grep de_DE

oldLocale = locale.setlocale(locale.LC_ALL) 
try:  # windows
    germanlocale = "German_Germany.1252"  
    locale.setlocale(locale.LC_ALL, germanlocale)
except locale.Error:
    germanlocale = False
try:  # linux (and others?)
    germanlocale = "de_DE.cp1252"
    locale.setlocale(locale.LC_ALL, germanlocale)
except locale.Error:
    germanlocale = False

class test_SavWriter_ioLocale(unittest.TestCase):

    def setUp(self):
        self.savFileName = os.path.join(tempfile.gettempdir(),
                                        "german_out.sav")
        self.kwargs = dict(savFileName=self.savFileName, 
                           varNames=[b'\xfcberhaupt'],
                           varTypes={b'\xfcberhaupt': 0},
                           ioLocale=germanlocale)

    @unittest.skipUnless(bool(germanlocale), "German locale not present")
    def test_locale_correct(self):    
        with SavWriter(**self.kwargs) as writer:
            writer.writerow([0])
        kwargs = dict(savFileName=self.savFileName, returnHeader=True,
                      ioLocale=germanlocale)
        with SavReader(**kwargs) as reader:
            varNames = next(reader)
            self.assertEqual(varNames, [b'\xfcberhaupt'])

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, oldLocale) 
        try:
            os.remove(self.savFileName)
        except EnvironmentError:
            raise(Exception, sys.exc_info()[1]) 

if __name__ == "__main__":
    unittest.main()

