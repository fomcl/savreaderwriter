#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import functools
from ctypes import c_char_p

isPy3k = sys.version_info[0] > 2

try:
    unicode
except NameError:
    basestring = unicode = str  # Python 3

try:
    xrange
except NameError:
    xrange = range

# bytes keyword has a second argument in Python 3
if isPy3k:
    bytes = functools.partial(bytes, encoding="utf-8")

# ctypes.c_char_p does not take unicode strings
if isPy3k:
    def c_char_py3k(s):
        s = s.encode("utf-8") if isinstance(s, str) else s
        return c_char_p(s)
else:
    def c_char_py3k(s):
        return c_char_p(s)
c_char_py3k.__doc__ = ("Wrapper for ctypes.c_char_p; in Python 3.x, s is converted to a utf-8 "
	               "encoded bytestring, in Python 2, it does nothing")

# Python 3: __unicode__ special method is now called __str__
# and __str__ is now called __bytes__
if isPy3k:
    def implements_to_string(cls):
        if "__str__" in cls.__dict__:
            cls.__dict__["__str__"].__name__ = "__bytes__"
            cls.__bytes__ = cls.__dict__["__str__"]
        if "__unicode__" in cls.__dict__:
            cls.__dict__["__unicode__"].__name__ = "__str__"
            cls.__str__ = cls.__dict__["__unicode__"]  
        return cls
else:
    implements_to_string = lambda cls: cls
implements_to_string.__doc__ = ("class decorator that replaces __unicode__ "
                                "and __str__ methods in Python 2 with __str__"
                                " and __bytes__ methods, respectively, in "
                                "Python 3")
