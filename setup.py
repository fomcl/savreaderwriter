#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python setup.py sdist --formats=gztar,zip bdist --formats=rpm,wininst
from distutils.core import setup
import os.path
import shutil

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
      url='https://bitbucket.org/fomcl/savReaderWriter',
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
