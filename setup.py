from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='savReaderWriter',
      version="3.1.1",
      description='Read and write SPSS files',
      author='Albert-Jan Roskam',
      author_email='fomcl@yahoo.com',
      license='MIT',
      long_description=read('README'),
      platforms='Windows, Mac, Linux',
      url='https://bitbucket.org/fomcl/savreaderwriter',
      py_modules=['__init__', 'error', 'generic', 'header', 
                  'savHeaderReader', 'savReader','savWriter'])

