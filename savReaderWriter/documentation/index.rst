.. savReaderWriter documentation master file, created by
   sphinx-quickstart on Thu Jan  3 00:25:18 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to savReaderWriter's documentation!
=================================================================================

.. module:: savReaderWriter
   :platform: Unix, Windows, Mac
   :synopsis: Read/Write Spss system files (.sav, .zsav)
.. moduleauthor:: Albert-Jan Roskam <fomcl@yahoo.com>

.. _`IBM SPSS Statistics Command Syntax Reference.pdf`: ftp://public.dhe.ibm.com/software/analytics/spss/documentation/statistics/20.0/en/client/Manuals/IBM_SPSS_Statistics_Command_Syntax_Reference.pdf
.. _`International License Agreement`: ./LA_en

In the documentation below, the associated SPSS commands are given in ``CAPS``.
See also the `IBM SPSS Statistics Command Syntax Reference.pdf`_ for info about SPSS syntax.

.. note::

   The :mod:`savReaderWriter` program uses the SPSS I/O module (``.so``, ``.dll``, ``.dylib``, depending on your Operating  System). Users of the SPSS I/O module should read the `International License Agreement`_ before using the SPSS I/O module. By downloading, installing, copying, accessing, or otherwise using the  SPSS I/O module, licensee agrees to the terms of this agreement. Copyright © IBM Corporation™ 1989, 2012 --- all rights reserved.


.. toctree::
   :maxdepth: 2

Installation
============================================================================

This program works for Linux (incl. z/Linux), Windows, MacOS (32 and 64 bit), AIX-64, HP-UX and Solaris-64. However, it has only been tested on Linux 32 (Ubuntu and Mint), Windows (mostly on Windows XP 32, but also a few times on Windows 7 64), and MacOS (with an earlier version of savReaderWriter). The other OSs are entirely untested. The program can be installed by running::

    python setup.py install

Or alternatively::

    pip install savReaderWriter

The ``cWriterow`` package is a faster Cython implementation of the pyWriterow method. To install it, you need Cython and run ``setup.py`` in the ``cWriterow`` folder::

    easy_install cython
    python setup.py build_ext --inplace

Windows
------------------------------------------------------------------------------
Depending on your architecture, you may add either the ``../spssio/win32`` or the ``../spssio/win64`` directory to ``PATH``, but this is *not* strictly necessary for the DLLs to be loaded properly. The search directory for the DLLs is set at run-time.

Linux
------------------------------------------------------------------------------
Additional files that were needed on my Linux 32-bit machine (Ubuntu 12 or Mint XFCE): intel-icc8-libs_8.0-1_i386.deb, libicu32_3.2-3_i386.deb, libstdc++5_3.3.6-20_i386.deb, libirc.so. Run the following commands in your terminal::

    sudo apt-get install intel-icc8-libs
    sudo apt-get install libicu32
    sudo apt-get install libstdc++5

To use the program, do something like::

    export LD_LIBRARY_PATH=/usr/local/lib/python2.7/dist-packages/savReaderWriter/spssio/lin32
    python wrapperForSavReaderWriter.py

A minimal wrapper would contain something like::

    from savReaderWriter import *
    with savReader("someFile.sav") as reader:
        for line in reader:
            pass

.. note::

    More code examples can be found in the ``doc_tests`` folder

You may also add the 'export' line to your ``.bashrc`` file::

    sudo gedit /etc/bash.bashrc

Other OS
------------------------------------------------------------------------------
As said, other OSs (except MacOS) are untested, but probably the logic is the same as for Linux. Use the following exports for MacOS, Solaris-64, AIX-64 and HP-UX, respectively::

    export DYLD_LIBRARY_PATH=/usr/local/lib/python2.7/dist-packages/savReaderWriter/spssio/macos
    export LD_LIBRARY_PATH=/usr/local/lib/python2.7/dist-packages/savReaderWriter/spssio/sol64
    export LIBPATH=/usr/local/lib/python2.7/dist-packages/savReaderWriter/spssio/aix64
    export SHLIB_PATH=/usr/local/lib/python2.7/dist-packages/savReaderWriter/spssio/hpux_it



:mod:`SavWriter` -- Write Spss system files
============================================================================
.. function:: SavWriter(savFileName, varNames, varTypes, [valueLabels=None, varLabels=None, formats=None, missingValues=None, measureLevels=None, columnWidths=None, alignments=None, varSets=None, varRoles=None, varAttributes=None, fileAttributes=None, fileLabel=None, multRespDefs=None, caseWeightVar=None, overwrite=True, ioUtf8=False, ioLocale=None, mode="wb", refSavFileName=None])
   
   **Write Spss system files (.sav, .zsav)**

   :param savFileName: the file name of the spss data file. File names that end with '.zsav' are   compressed using the ZLIB (ZSAV) compression scheme (requires v21 SPSS I/O files), while for file    names that end with '.sav' the 'old' compression scheme is used (it is not possible to generate uncompressed files unless you modify the source code).

   :param varNames: list of the variable names in the order in which they appear in the spss data file.

   :param varTypes: varTypes dictionary ``{varName: varType}``, where varType == 0 means 'numeric', and varType > 0 means 'character' of that length (in bytes)

   :param valueLabels: value label dictionary ``{varName: {value: label}}``. Cf. ``VALUE LABELS`` (default: None).

   :param varLabels: variable label dictionary ``{varName: varLabel}``. Cf. ``VARIABLE LABEL`` (default: None).

   :param formats: print/write format dictionary ``{varName: spssFmt}``. Commonly used formats include F  (numeric, e.g. F5.4), N (numeric with leading zeroes, e.g. N8), A (string, e.g. A8) and EDATE/ADATE  (European/American date, e.g. ADATE30). Cf. ``FORMATS`` (default: None).

   :param missingValues: missing values dictionary ``{varName: {missing_value_spec}}``. Cf. ``MISSING VALUES`` (default: None). For example: 

      .. code:: python

         missingValues = {"someNumvar1": {"values": [999, -1, -2]},  # discrete values
                          "someNumvar2": {"lower": -9, "upper": -1}, # range, cf. MISSING VALUES x (-9 THRU -1)
                          "someNumvar3": {"lower": -9, "upper": -1, "value": 999},
                          "someStrvar1": {"values": ["foo', "bar", "baz"]},
                          "someStrvar2": {"values': "bletch"}}
     
      .. note:: *measureLevels, columnWidths, alignments must all three be set, if used*

   :param measureLevels: measurement level dictionary ``{varName: <level>}``. Valid levels are: "unknown",  "nominal", "ordinal", "scale", "ratio", "flag", "typeless". Cf. ``VARIABLE LEVEL`` (default: None). 

   :param columnWidths: column display width dictionary ``{varName: <int>}``. Cf. ``VARIABLE WIDTH``.   (default: None --> >= 10 [stringVars] or automatic [numVars]). 

   :param alignments: alignment dictionary ``{varName: <left/center/right>}`` Cf. ``VARIABLE ALIGNMENT``  (default: None --> numerical: right, string: left). 

   :param varSets: sets dictionary ``{setName: [list_of_valid_varNames]}``. Cf. ``SETMACRO`` extension  command. (default: None). 

   :param varRoles: variable roles dictionary ``{varName: varRole}``. VarRoles may be any of the following:  'both', 'frequency', 'input', 'none', 'partition', 'record ID', 'split', 'target'. Cf. ``VARIABLE ROLE``  (default: None). 

   :param varAttributes: variable attributes dictionary ``{varName: {attribName: attribValue}`` (default:  None). Cf. ``VARIABLE  ATTRIBUTES``. (default: None). For example:

      .. code:: python

         varAttributes = {'gender': {'Binary': 'Yes'}, 'educ': {'DemographicVars': '1'}}

   :param fileAttributes: file attributes dictionary ``{attribName: attribValue}``. Square brackets indicate  attribute arrays, which must  start with 1. Cf. ``FILE ATTRIBUTES``. (default: None). For example:

      .. code:: python

         fileAttributes = {'RevisionDate[1]': '10/29/2004', 'RevisionDate[2]': '10/21/2005'} 

   :param fileLabel: file label string, which defaults to "File created by user <username> at <datetime>" if  file label is None. Cf. ``FILE LABEL`` (default: None). 

   :param multRespDefs: Multiple response sets definitions (dichotomy groups or category groups) dictionary ``{setName: <set definition>}``. In SPSS syntax, 'setName' has a dollar prefix ('$someSet'). See also  docstring of multRespDefs method. Cf. ``MRSETS``. (default: None). 

   :param caseWeightVar: valid varName that is set as case weight. Cf. ``WEIGHT BY`` command). 

   :param overwrite: Boolean that indicates whether an existing Spss file should be overwritten (default: True). 

   :param ioUtf8: Boolean that indicates the mode in which text communicated to or from the I/O Module will  be. Valid values are True (UTF-8/unicode mode, cf. ``SET UNICODE=ON``) or False (Codepage mode, ``SET  UNICODE=OFF``) (default: False). 

   :param ioLocale: indicates the locale of the I/O module, cf. ``SET LOCALE`` (default: None, which is the  same as ``".".join(locale.getlocale())``. Locale specification is OS-dependent. 

   :param mode: indicates the mode in which <savFileName> should be opened. Possible values are "wb" (write),  "ab" (append), "cp" (copy: initialize header using <refSavFileName> as a reference file, cf. ``APPLY DICTIONARY``). (default: "wb"). 

   :param refSavFileName: reference file that should be used to initialize the header (aka the SPSS data  dictionary) containing variable label, value label, missing value, etc, etc definitions. Only relevant  in conjunction with mode="cp". (default: None). 


Typical use::
    
    savFileName = "someFile.sav"
    records = [['Test1', 1, 1], ['Test2', 2, 1]]
    varNames = ['var1', 'v2', 'v3']
    varTypes = {'var1': 5, 'v2': 0, 'v3': 0}
    with SavWriter(savFileName, varNames, varTypes) as sav:
        for record in records:
            sav.writerow(record)

.. note::

    More code examples can be found in the ``doc_tests`` folder

:mod:`SavReader` -- Read Spss system files
============================================================================
.. function:: SavReader(savFileName, [returnHeader=False, recodeSysmisTo=None,                 verbose=False, selectVars=None, idVar=None, rawMode=False, ioUtf8=False, ioLocale=None])

   **Read Spss system files (.sav, .zsav)**

   :param savFileName: the file name of the spss data file

   :param returnHeader: Boolean that indicates whether the first record should be a list of variable names (default = False)

   :param recodeSysmisTo: indicates to which value missing values should be recoded (default = None, i.e. no recoding is done)

   :param selectVars: indicates which variables in the file should be selected. The variables should be  specified as a list or a tuple of valid variable names. If None is specified, all variables in the file are used (default = None)

   :param idVar: indicates which variable in the file should be used for use as id variable for the 'get'  method (default = None)

   :param verbose: Boolean that indicates whether information about the spss data file (e.g., number of cases,  variable names, file size) should be printed on the screen (default = False).

   :param rawMode: Boolean that indicates whether values should get SPSS-style formatting, and whether date variables (if present) should be converted to ISO-dates. If True, the program does not format any values, which increases processing speed. (default = False)

   :param ioUtf8: Boolean that indicates the mode in which text communicated to or from the I/O Module will be. Valid values are True (UTF-8 mode aka Unicode mode) and False (Codepage mode). Cf. ``SET UNICODE=ON/OFF`` (default = False)

   :param ioLocale: indicates the locale of the I/O module. Cf. ``SET LOCALE`` (default = None, which corresponds to ``".".join(locale.getlocale())``)

.. warning::

   Once a file is open, ``ioUtf8`` and ``ioLocale`` can not be changed. The same applies after a file could not be successfully closed. Always ensure a file is closed by calling ``__exit__()`` (i.e., using a context manager) or ``close()`` (in a ``try - finally`` suite)

Typical use::
    
    savFileName = "someFile.sav"
    with SavReader(savFileName, returnHeader=True) as sav:
        header = sav.next()
        for line in sav:
            process(line)

Use of __getitem__ and other methods		::
    
    reader = SavReader(savFileName, idVar="id")
    try:
        print "The file contains %d records" % len(reader)
        print unicode(reader)  # prints a file report
        print "The first six records look like this\n", reader[:6]
        print "The first record looks like this\n", reader[0]
        print "The last four records look like this\n", reader.tail(4)
        print "The first five records look like this\n", reader.head()
        print "First column:\n", reader[..., 0]  # requires numpy
        print "Row 4 & 5, first three cols\n", reader[4:6, :3]  # requires numpy
        ## ... Do a binary search for records --> idVar
        print reader.get(4, "not found")             # gets 1st record where id==4
    finally:
        reader.close()

.. note::

    More code examples can be found in the ``doc_tests`` folder

:mod:`SavHeaderReader` -- Read Spss file meta data
============================================================================
.. function:: SavHeaderReader(savFileName[, ioUtf8=False, ioLocale=None])
	
   **Read Spss file meta data. Yields the same information as the Spss command ``DISPLAY DICTIONARY``**


   :param savFileName: the file name of the spss data file

   :param ioUtf8: Boolean that indicates the mode in which text communicated to or from the I/O Module will be. Valid values are True (UTF-8 mode aka Unicode mode) and False (Codepage mode). Cf. ``SET UNICODE=ON/OFF`` (default = False)

   :param ioLocale: indicates the locale of the I/O module. Cf. ``SET LOCALE`` (default = None, which corresponds to ``".".join(locale.getlocale())``)

.. warning::

   The program calls ``spssFree*`` C functions to free memory allocated to dynamic arrays. This previously sometimes caused segmentation faults. This problem now appears to be solved. However, if you do experience segmentation faults you can set ``segfaults=True`` in ``__init__.py``. This will prevent the spssFree* functions from being called (and introduce a memory leak).

Typical use::

    with SavHeaderReader(savFileName) as spssDict:
        wholeDict = spssDict.dataDictionary()
        print unicode(spssDict)

.. note::

    More code examples can be found in the ``doc_tests`` folder

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

