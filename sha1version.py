#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

path = os.path.dirname(os.path.realpath("__file__"))

def callShell(cmd, cwd=path):
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = proc.communicate()
    if not stderr:
        stdout = stdout.split(b"\n")
        try:
            return [item.decode("utf-8") for item in stdout]
        except:
            return stdout
    return []

def getHEADhash(strict=False, cwd=path):
    """Returns a label for the HEAD revision of a Git repository. The label has
    the form <tag>-<SHA1 hash>-dirty. The '-dirty' suffix is only present if
    there are uncommitted changes. If strict, raise ValueError in case of
    untagged and/or dirty files. Example output:
    v1.0.1-fb74f0a6caf0385918b6971c6248977e97662a93-dirty"""
    tags = callShell("git tag -l", cwd)
    taglookup = {callShell("git rev-parse %s" % tag, cwd)[0]: tag for \
                 tag in tags}
    head_hash = callShell("git rev-parse HEAD", cwd)[0]
    isDirty = bool(callShell("git status -s")[0])
    isTagged = bool(taglookup.get(head_hash))
    if isTagged:
        label = "%s-%s" % (tags.get(head_hash), head_hash)
    else:
        label = "untagged-%s" % head_hash
    if isDirty:
        label += "-dirty"
    label = label if label != "untagged-" else "UNKNOWN"
    if strict:
        if isDirty or not isTagged or label == "UNKNOWN":
            raise ValueError("Problem determining version: %r" % label)
    if sys.version_info[0] > 2:
        return bytes(label, "utf-8")
    return label

if __name__ == "__main__":
    with open(os.path.join(path, "SHA1VERSION"), "wb") as f:
        f.write(getHEADhash())
