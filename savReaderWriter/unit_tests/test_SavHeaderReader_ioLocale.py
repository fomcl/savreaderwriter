#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Q: "variable names with non-ASCII characters are returned as v1, v2, v3, etc"
# A: Assuming the file was created in codepage mode (default in SPSS until 
#    very recently), setting ioLocale to the proper (OS-dependent) locale 
#    specification should do the trick. Note that the I/O has its own locale:
#    the locale of the host system is not affected. I had to generate a German
#    locale with the (Windows) codepage 1252 on my Linux machine first
#    http://documentation.basis.com/BASISHelp/WebHelp/inst/character_encoding.htm
#    sudo localedef -f CP1252 -i de_DE /usr/lib/locale/de_DE.cp1252
#    locale -a | grep de_DE
# Python 2.7.3 (default, Apr 10 2013, 05:09:49) [GCC 4.7.2] on linux2

import unittest
import sys
import locale

from savReaderWriter import *


class test_SavHeaderReader_ioLocale(unittest.TestCase):

    def setUp(self):
        self.expected = [b'python', b'programmieren', b'macht',
                         b'\xfcberhaupt', b'v\xf6llig', b'spa\xdf']
        self.savFileName = "test_data/german.sav"
        self.is_windows = sys.platform.startswith("win")
	# any locale will do as long as the encoding is cp1252.
        # iso-8859-1 and latin-1 will probably also do.
        if self.is_windows:
            self.ioLocale = "German_Germany.1252"
        else:
            self.ioLocale = "de_DE.cp1252"

    def test_locale_correct(self):
        """ioLocale is specified, which is required only if file encoding
        and encoding of host locale incompatible, e.g. a .sav file that was
        created under Windows using cp1252 encoding is accessed under Linux
        using utf-8 encoding"""
        with SavHeaderReader(self.savFileName, 
                             ioLocale=self.ioLocale) as header:
            self.assertEqual(header.varNames, self.expected)
            self.assertTrue(header.isCompatibleEncoding())

    def test_locale_incorrect(self):
        """Host locale is incompatible with file encoding; ioLocale not
        specified. This causes accented variable names to be replaced with
        v1, v2, v3, ..., v<n> because ioLocale is not compatible with file
        locale (codepage). If not specified, ioLocale is initialized to the
        host locale"""
        wrong = [b'python', b'programmieren', b'macht', b'v1', b'v2', b'v3']
        codepage = locale.setlocale(locale.LC_ALL).split(".")[-1]
        incompatible = codepage not in self.ioLocale
        if incompatible:
            with SavHeaderReader(self.savFileName) as header:
                self.assertNotEqual(header.varNames, self.expected)
                self.assertEqual(header.varNames, wrong)
                self.assertFalse(header.isCompatibleEncoding())

if __name__ == "__main__":
    unittest.main()

