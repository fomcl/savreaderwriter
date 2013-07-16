#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import warnings
from savReaderWriter import retcodes

class SPSSIOError(Exception):
    """
    Error class for the IBM SPSS Statistics Input Output Module
    """
    def __init__(self, msg=u"Unknown", retcode=None):
        self.retcode = retcode
        Exception.__init__(self, msg)

class SPSSIOWarning(UserWarning):
    """
    Warning class for the IBM SPSS Statistics Input Output Module

    If the environment variable SAVRW_DISPLAY_WARNS is undefined or 0
    (False) warnings are ignored. If it is 1 (True) warnings (non-fatal
    exceptions) are displayed once for every location where they occur.
    """
    pass

# Warnings are usually harmless!
env = os.environ.get("SAVRW_DISPLAY_WARNS")
SAVRW_DISPLAY_WARNS = bool(int(env)) if str(env).isdigit() else False
action = "default" if SAVRW_DISPLAY_WARNS else "ignore"
warnings.simplefilter(action, SPSSIOWarning)

def checkErrsWarns(msg, retcode):
    """Throws a warning if retcode < 0 (and warnings are not ignored),
    and throws an error if retcode > 0. Returns None if retcode == 0"""
    if not retcode:
        return
    msg += " [%s]" % retcodes.get(retcode, retcode)
    if retcode > 0:
        raise SPSSIOError(msg, retcode)
    elif retcode < 0:
        warnings.warn(msg, SPSSIOWarning, stacklevel=2)