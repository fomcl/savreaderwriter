from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options
import os

try:
    os.chdir(os.path.dirname(__file__))  # tox
except OSError:
    pass

Cython.Compiler.Options.annotate = True
setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("cWriterow", ["cWriterow.pyx"])]
    )
