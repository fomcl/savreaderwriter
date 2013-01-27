#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python setup.py sdist --formats=gztar,zip bdist --formats=rpm,wininst
from distutils.core import setup
import os.path

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()

#      py_modules=['__init__', 'error', 'generic', 'header',
#                  'savHeaderReader', 'savReader','savWriter'],
email = "@".join(["fomcl", "yahoo.com"])

spssio = ['include/*.*', 'win64/*.*', 'macos/*.*', 'win32/*.*', 'sol64/*.*', 'lin32/*.*', 'lin64/*.*', 
          'documents/*.*', 'hpux_it/*.*', 'zlinux64/*.*', 'aix64/*.*', 'license/*.*']

spssio = ['spssio/include/*.*', 'spssio/win64/*.*', 'spssio/macos/*.*', 
          'spssio/win32/*.*', 'spssio/sol64/*.*', 'spssio/lin32/*.*', 
          'spssio/lin64/*.*', 'spssio/documents/*.*', 'spssio/hpux_it/*.*', 
          'spssio/zlinux64/*.*', 'spssio/aix64/*.*', 'spssio/license/*.*']
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
      url='https://bitbucket.org/fomcl/savReaderWriter',
      packages=['savReaderWriter'],
      package_data={'savReaderWriter': spssio + ['cWriterow/*.*', 'documentation/*.*', 'build/*.*']},
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

