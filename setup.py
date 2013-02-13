#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python setup.py sdist --formats=gztar,zip bdist --formats=rpm,wininst
# sudo python setup.py register -r https://testpypi.python.org/pypi sdist --formats=gztar bdist --formats=egg upload -r https://testpypi.python.org/pypi

#from distutils.core import setup

import os
import shutil
import sys

sys.path.append(os.path.abspath("."))
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()

email = "@".join(["fomcl", "yahoo.com"])

setup(name='savReaderWriter',
      version=read('VERSION'),
      description='Read and write SPSS files',
      author='Albert-Jan Roskam',
      author_email=email,
      maintainer='Albert-Jan Roskam',
      maintainer_email=email,
      license='MIT',
      long_description=read('README'),
      platforms=['Windows', 'Mac', 'Linux/POSIX'],
      url='https://bitbucket.org/fomcl/savreaderwriter',
      packages=['savReaderWriter'],
      package_data={'savReaderWriter': ['spssio/include/*.*',
                                        'spssio/win64/*.*',
                                        'spssio/macos/*.*',
                                        'spssio/win32/*.*',
                                        'spssio/sol64/*.*',
                                        'spssio/lin32/*.*',
                                        'spssio/lin64/*.*',
                                        'spssio/documents/*.*',
                                        'spssio/hpux_it/*.*',
                                        'spssio/zlinux64/*.*',
                                        'spssio/aix64/*.*',
                                        'spssio/license/*.*',
                                        'cWriterow/*.*',
                                        'documentation/*',
                                        'doc_tests/*.*',
                                        'test_data/*.*',
                                        'README','VERSION', 
                                        'TODO', 'COPYRIGHT']},
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: MacOS',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX',
                   'Programming Language :: Cython',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Topic :: Database']
      )

# ugly, but it works
for f in ['README','VERSION', 'TODO', 'COPYRIGHT']:
    p = os.path.dirname(__file__)
    src = os.path.join(p, f)
    dst = os.path.join(p, "savReaderWriter", f)
    shutil.copy(src, dst)
