#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python setup.py sdist --formats=gztar,zip bdist --formats=rpm,wininst
# sudo python setup.py register -r https://testpypi.python.org/pypi sdist --formats=gztar bdist --formats=egg upload -r https://testpypi.python.org/pypi

import os
import shutil
import sys
import platform

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()

#####
## Set package_data values, depending on install/build
#####
args = sys.argv
is_32bit = platform.architecture()[0] == "32bit"
is_install_mode = 'install' in args
is_only_bdist = 'bdist' in args and not 'sdist' in args
is_msi32 = is_only_bdist and '--formats=wininst' in args
is_rpm32 = is_only_bdist and '--formats=rpm' in args  
pf = sys.platform.lower()

## This is included in every platform
package_data = {'savReaderWriter': ['spssio/include/*.*',
                                    'spssio/documents/*',
                                    'spssio/license/*',
                                    'cWriterow/*.*',
                                    'documentation/*',
                                    'doc_tests/*.*',
                                    'test_data/*.*',
                                    'README','VERSION', 
                                    'TODO', 'COPYRIGHT']}

## *installing* the package: install only platform-relevant libraries
if is_install_mode:             
    if pf.startswith("win") and is_32bit:
        package_data['savReaderWriter'].append('spssio/win32/*.*')
    elif pf.startswith("win"):
        package_data['savReaderWriter'].append('spssio/win64/*.*')
    # How to recognize zLinux (IBM System Z)???
    elif pf.startswith("lin") and is_32bit:
        package_data['savReaderWriter'].append('spssio/lin32/*.*')
    elif pf.startswith("lin"):
        package_data['savReaderWriter'].append('spssio/lin64/*.*')
    elif pf.startswith("darwin") or pf.startswith("mac"):
        package_data['savReaderWriter'].append('spssio/macos/*.*')
    elif pf.startswith("aix") and not is_32bit:
        package_data['savReaderWriter'].append('spssio/aix64/*.*')
    elif pf.startswith("hp-ux"):
        package_data['savReaderWriter'].append('spssio/hp-ux/*.*')
    elif pf.startswith("sunos") and not is_32bit:
        package_data['savReaderWriter'].append('spssio/sol64/*.*')
    else:
        msg = "Your platform (%r) is not supported" % pf
        raise NotImplementedError(msg)

## Two 'light-weight' binary distributions
elif is_rpm32:
    package_data['savReaderWriter'].append('spssio/lin32/*.*')

elif is_msi32:
    package_data['savReaderWriter'].append('spssio/win32/*.*')

## *building* the package: include all the libraries
else: 
    package_data['savReaderWriter'].extend(['spssio/win64/*.*',
                                            'spssio/macos/*.*',
                                            'spssio/win32/*.*',
                                            'spssio/sol64/*.*',
                                            'spssio/lin32/*.*',
                                            'spssio/lin64/*.*',
                                            'spssio/hpux_it/*.*',
                                            'spssio/zlinux64/*.*',
                                            'spssio/aix64/*.*'])

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
      zip_safe=False,
      platforms=['Windows', 'Mac', 'Linux/POSIX'],
      url='https://bitbucket.org/fomcl/savreaderwriter',
      download_url='https://bitbucket.org/fomcl/savreaderwriter/downloads',
      extras_require={'fastReading': ["psyco"],
                      'arraySlicing': ["numpy"],
                      'fastWriting': ["Cython"],},
      packages=['savReaderWriter'],
      package_data=package_data,
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
