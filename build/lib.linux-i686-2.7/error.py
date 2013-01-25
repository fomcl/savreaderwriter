#!/usr/bin/env python
# -*- coding: utf-8 -*-

from savReaderWriter import *

class SPSSIOError(Exception):
    """
    Error class for the IBM SPSS Statistics Input Output Module
    """

    def __init__(self, msg=u"Unknown", retcode=None):
        if isinstance(retcode, int):
            code = retcodes.get(retcode, retcode)
        elif isinstance(retcode, list):
            code = ", ".join([retcodes.get(retcodex) for retcodex in retcode])
        else:
            code = "unknown code %r" % retcode
        msg = "%s [retcode: %r]" % (msg, code)
        Exception.__init__(self, msg)
