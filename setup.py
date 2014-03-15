#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python setup.py sdist --formats=gztar,zip bdist --formats=rpm,wininst
# sudo python setup.py register -r https://testpypi.python.org/pypi sdist --formats=gztar bdist --formats=egg upload -r https://testpypi.python.org/pypi
# sudo python setup.py check build_sphinx --source-dir=savReaderWriter/documentation -v
# sudo python setup.py check upload_sphinx --upload-dir=build/sphinx/html

import os
import sys
import platform

path = os.path.dirname(os.path.realpath(__file__)) or os.getcwd()
sys.path.insert(0, path)

try:
    from ez_setup import use_setuptools
    use_setuptools()
except:
    pass # Tox
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()

#####
## Set package_data values, depending on install/build
#####

is_32bit = platform.architecture()[0] == "32bit"
is_64bit = platform.architecture()[0] == "64bit"
is_install_mode = 'install' in sys.argv
pf = sys.platform.lower()

## This is included in every platform
package_data = {'savReaderWriter': ['spssio/include/*.*',
                                    'spssio/documents/*',
                                    'spssio/license/*',
                                    'cWriterow/*.*',
                                    'documentation/*.*',
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
    elif pf.startswith("lin") and is_32bit:
        package_data['savReaderWriter'].append('spssio/lin32/*.*')
    elif pf.startswith("lin") and is_64bit and os.uname()[-1] == "s390x":
        package_data['savReaderWriter'].append('spssio/zlinux64/*.*')
    elif pf.startswith("lin") and is_64bit:
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

## *building* the package: include all the libraries
else: 
    package_data['savReaderWriter'].extend(['spssio/win32/*.*',
                                            'spssio/win64/*.*',
                                            'spssio/lin32/*.*',
                                            'spssio/zlinux64/*.*',
                                            'spssio/lin64/*.*',
                                            'spssio/macos/*.*',
                                            'spssio/aix64/*.*'
                                            'spssio/hpux_it/*.*',
                                            'spssio/sol64/*.*'])

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
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3', 
                   'Programming Language :: Cython',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Topic :: Database']
      )

# ugly, but it works
# for f in ['README','VERSION', 'TODO', 'COPYRIGHT']:
#     p = os.path.dirname(__file__)
#     src = os.path.join(p, f)
#     dst = os.path.join(p, "savReaderWriter", f)
#     shutil.copy(src, dst)

with open(os.path.join(path, "savReaderWriter", "SHA1VERSION"), "wb") as f:
    try:
        import sha1version
        f.write(sha1version.getHEADhash())
    except:
        f.write(b"--UNKNOWN--")
