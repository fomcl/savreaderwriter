#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import functools
from ctypes import c_char_p

isPy3k = sys.version_info[0] == 3

try:
    unicode
except NameError:
    basestring = unicode = str  # Python 3

try:
    xrange
except NameError:
    xrange = range

if isPy3k:
    bytes = functools.partial(bytes, encoding="utf-8")

def c_char_p_(s):
    """Wrapper for ctypes.c_char_p; in Python 3.x, s is converted to a utf-8
    encoded bytestring"""
    if not isPy3k:
        # # for now, keep this, but later change this so Python 2.7 also takes unicode strings as args
        return c_char_p(s)
    else:
        print("&&&&&  %s" % s)
        s = s.encode("utf-8") if isinstance(s, str) else s
        print("-----------> %s" % type(s))
        return c_char_p(s)

