#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

def memoized_property(fget):
    """
    Return a property attribute for new-style classes that only calls its 
    getter on the first access. The result is stored and on subsequent 
    accesses is returned, preventing the need to call the getter any more.
    source: https://pypi.python.org/pypi/memoized-property/1.0.1
    """
    attr_name = "_" + fget.__name__
    @wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)
    return property(fget_memoized)

def memoize(f):
    """Memoization decorator
    source: http://code.activestate.com/recipes/577219-minimalistic-memoization/"""
    # see also issue # 22 
    cache = {}
    MAXCACHE = 10 ** 7
    @wraps(f)
    def memf(*datetime):
        if datetime in cache:
            return cache[datetime]
        elif len(cache) < MAXCACHE:
            result = f(*datetime)
            cache[datetime] = result
            return result
        return f(*datetime)
    return memf 
