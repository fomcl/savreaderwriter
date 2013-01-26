#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python setup.py sdist --formats=gztar,zip bdist --formats=rpm,wininst
from distutils.core import setup
import os.path

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def version(fname='VERSION'):
    p = os.path.realpath(__file__)
    return open(os.path.join(os.path.dirname(p), fname)).read().strip()

setup(name='savReaderWriter',
      version='3.1.1',
      description='Read and write SPSS files',
      author='Albert-Jan Roskam',
      author_email='fomcl@yahoo.com',
      maintainer='Albert-Jan Roskam',
      maintainer_email='fomcl@yahoo.com',
      license='MIT',
      long_description=read('README'),
      platforms=['Windows', 'Mac', 'Linux/POSIX'],
      url='https://bitbucket.org/fomcl/savReaderWriter',
      py_modules=['__init__', 'error', 'generic', 'header',
                  'savHeaderReader', 'savReader','savWriter'],
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

