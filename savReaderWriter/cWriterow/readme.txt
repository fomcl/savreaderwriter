# cWriterow is a faster C version of the Python pyWriterow method.
# It requires that Cython + a C compiler be installed (http://docs.cython.org/src/quickstart/install.html)		

```
easy_install cython  # requires setuptools
python setup.py build_ext --inplace
```

*Note for Windows*
If you get an error `"Unable to find vcvarsall.bat".`, try the following (assumes path of `gcc.exe` is on your `PATH`):

```
python.exe setup.py build_ext --inplace --compiler=mingw32
```