#!/usr/bin/env python
# -*- coding: utf-8 -*-

# see: http://bugs.python.org/issue23425
import locale
from ctypes import *
from ctypes.wintypes import *

LOCALE_WINDOWS = 1
LOCALE_SENGLISHLANGUAGENAME = 0x1001
LOCALE_SENGLISHCOUNTRYNAME = 0x1002
LOCALE_IDEFAULTANSICODEPAGE = 0x1004
LCTYPES = (LOCALE_SENGLISHLANGUAGENAME,
           LOCALE_SENGLISHCOUNTRYNAME,
           LOCALE_IDEFAULTANSICODEPAGE)

kernel32 = WinDLL('kernel32')
EnumSystemLocalesEx = kernel32.EnumSystemLocalesEx
GetLocaleInfoEx = kernel32.GetLocaleInfoEx

EnumLocalesProcEx = WINFUNCTYPE(BOOL, LPWSTR, DWORD, LPARAM)

def enum_system_locales():
    alias = {}
    codepage = {}
    info = (WCHAR * 100)()

    @EnumLocalesProcEx
    def callback(locale, flags, param):
        if '-' not in locale:
            return True
        parts = []
        for lctype in LCTYPES:
            if not GetLocaleInfoEx(locale,
                                   lctype,
                                   info, len(info)):
                raise WinError()
            parts.append(info.value)
        lang, ctry, code = parts
        if lang and ctry and code != '0':
            locale = locale.replace('-', '_')
            full = u'{}_{}'.format(lang, ctry)
            alias[locale] = full
            codepage[locale] = code
        return True
   
    if not EnumSystemLocalesEx(callback,
                               LOCALE_WINDOWS,
                               None, None):
        raise WinError()
    return alias, codepage

def resetlocale():
    unixlocale = locale.getdefaultlocale()[0]
    alias, codepage = enum_system_locales()
    language = alias.get(unixlocale, "en_US")
    codepage = codepage.get(unixlocale, "cp1252")
    locale.setlocale(locale.LC_ALL, (language, codepage))

if __name__ == "__main__":
    alias, codepage = enum_system_locales()
