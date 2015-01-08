.. savReaderWriter documentation master file, created by
   sphinx-quickstart on Thu Jan  3 00:25:18 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to savReaderWriter's documentation!
=================================================================================

.. module:: savReaderWriter
   :platform: Linux, Windows, Mac OS, HP-UX, AIX, Solaris, zLinux
   :synopsis: Read/Write SPSS system files (.sav, .zsav)
.. moduleauthor:: Albert-Jan Roskam

.. _`IBM SPSS Statistics Command Syntax Reference.pdf`: ftp://public.dhe.ibm.com/software/analytics/spss/documentation/statistics/20.0/en/client/Manuals/IBM_SPSS_Statistics_Command_Syntax_Reference.pdf
.. _`International License Agreement`: ./_static/LA_en.txt
.. _`OS X and Python locale snippet`: ./_static/mac_os_x_locale_quirks.txt

In the documentation below, the associated SPSS commands are given in ``CAPS``.
See also the `IBM SPSS Statistics Command Syntax Reference.pdf`_ for info about SPSS syntax.

.. raw:: html

    <embed>
    </p>I always appreciate getting
    <script type="text/javascript" language="javascript">
    <!--
    // Email obfuscator script 2.1 by Tim Williams, University of Arizona
    // Random encryption key feature by Andrew Moulden, Site Engineering Ltd
    // This code is freeware provided these four comment lines remain intact
    // A wizard to generate this code is at http://www.jottings.com/obfuscator/
    { coded = "KNMT1@S8oNN.TNM"
      key = "NVXDIRH5nwJ1dLckfsjZFzbCv79xYTWKh3qytUuam0O4PpioEASG628MerlQgB"
      shift=coded.length
      link=""
      for (i=0; i<coded.length; i++) {
        if (key.indexOf(coded.charAt(i))==-1) {
          ltr = coded.charAt(i)
          link += (ltr)
        }
        else {     
          ltr = (key.indexOf(coded.charAt(i))-shift+key.length) % key.length
          link += (key.charAt(ltr))
        }
      }
    document.write("<a href='mailto:"+link+"?subject=feedback on savReaderWriter'>feedback</a>")
    }
    //-->
    </script><noscript>Sorry, you need Javascript on to email me.</noscript>
    on this package, so I can keep improving it!</p>
    </embed>

.. seealso::

   The :mod:`savReaderWriter` program uses the SPSS I/O module (``.so``, ``.dll``, ``.dylib``, depending on your Operating  System). Users of the SPSS I/O
   module should read the `International License Agreement`_ before using the SPSS I/O module. By downloading, installing, copying, accessing, or otherwise
   using the  SPSS I/O module, licensee agrees to the terms of this agreement. Copyright © IBM Corporation™ 1989, 2012 --- all rights reserved.

Installation
============================================================================

Platforms
----------
As shown in **Table 0** below, this program works for Linux (incl. z/Linux), Windows, Mac OS (32 and 64 bit), AIX-64, HP-UX and Solaris-64. The program has been tested with Python 2.7, 3.3 and 3.4 on Debian Linux (32 and 64 bit), Mac OS and Windows 7 (64 bit).

.. exceltable:: **Table 0.** supported platforms for ``savReaderWriter`` 
   :file: ./platforms.xls
   :header: 2
   :selection: A1:C9

Setup
-------------------
The program can be installed by running::

    python setup.py install

Or alternatively::

    pip install savReaderWriter --allow-all-external

To get the 'bleeding edge' version straight from the repository do::

    pip install -U -e git+https://bitbucket.org/fomcl/savreaderwriter.git#egg=savreaderwriter


.. note::

   **Users of Mac OS X** need to do two additional things:

   * ``DYLD_LIBRARY_PATH`` needs to be set to the directory where the SPSS I/O libraries for Mac OS X live. If you also set ``LC_ALL`` environment variable, you may skip the next ``ioLocale`` step. You may also want to edit your ``~/.bashrc`` accordingly. 
   * ``ioLocale`` needs to be set manually (work-around). The ``ioLocale`` is the locale of the SPSS I/O, which is supposed to be copied from the host system, if unset (i.e., equal to ``None``). However, Python ``locale.setlocale`` and ``locale.getlocale`` are `quirky in Mac OS X <http://bugs.python.org/issue18378>`_ (see also this `OS X and Python locale snippet`_). 

   The code below shows an example that uses Python 2.7.2 (Python 3.3.5 also works) under Mac OS X Mountain Lion 10.9.1: 

   .. code:: sh

      fomcls-Mac-Pro:~ fomcl$ uname -a
      Darwin fomcls-Mac-Pro.local 12.2.0 Darwin Kernel Version 12.2.0: Sat Aug 25 00:48:52 PDT 2012; root:xnu-2050.18.24~1/RELEASE_X86_64 x86_6
      fomcls-Mac-Pro:~ fomcl$ export DYLD_LIBRARY_PATH=/Library/Python/2.7/site-packages/savReaderWriter/spssio/macos
      fomcls-Mac-Pro:~ fomcl$ export LC_ALL=en_US.UTF-8  # if you also do this, specifiying ioLocale is usually not needed
      fomcls-Mac-Pro:savReaderWriter fomcl$ python
      Python 2.7.2 (default, Jun 20 2012, 16:23:33) [GCC 4.2.1 Compatible Apple Clang 4.0 (tags/Apple/clang-418.0.60)] on darwin
      >>> import savReaderWriter
      >>> savFileName = "/Library/Python/2.7/site-packages/savReaderWriter/test_data/Employee data.sav"
      >>> with savReaderWriter.SavReader(savFileName, ioLocale='en_US.UTF-8') as reader:
      ...     for line in reader:
      ...         print line
      ... 
      [1.0, 'm', '1952-02-03', 15.0, 3.0, 57000.0, 27000.0, 98.0, 144.0, 0.0]
      [2.0, 'm', '1958-05-23', 16.0, 1.0, 40200.0, 18750.0, 98.0, 36.0, 0.0]
      [3.0, 'f', '1929-07-26', 12.0, 1.0, 21450.0, 12000.0, 98.0, 381.0, 0.0]
      [4.0, 'f', '1947-04-15', 8.0, 1.0, 21900.0, 13200.0, 98.0, 190.0, 0.0]
      # etc. etc.

.. versionchanged:: 3.4

* Added ``SavReaderNp``, a class to convert .sav files to numpy arrays
* Added ``savViewer``, a PyQt4-based script to view .sav, .xls, .xlsx, .csv, .tab files
* Removed several bugs, notably one related to memoization of SPSS datetimes

.. versionchanged:: 3.3

* The ``savReaderWriter`` program now runs on Python 2 and 3. It is tested with Python 2.7, 3.3 and PyPy under Debian Linux 3.2.0-4-AMD64.
* Under Python 3.3, the data are in ``bytes``! Use the b' prefix when writing string data, or write data in unicode mode (``ioUtf8=True``).
* Several bugs were removed, notably two that prevented the I/O modules from loading in 64-bit Linux and 64-bit Windows systems (NB: these bugs were entirely unrelated). I re-downloaded the SPSS I/O v21 FP1 modules because the Win 64 libs were incorrectly compiled. In addition, long variable labels were truncated to 120 characters, which is now fixed.
* This has not yet been tested for performance.

.. versionchanged:: 3.2

* The ``savReaderWriter`` program is now self-contained. That is, the IBM SPSS I/O modules now all load by themselves, without any changes being required anymore to ``PATH``, ``LD_LIBRARY_PATH`` and equivalents. Also, no extra .deb files need to be installed anymore (i.e. no dependencies). 

* ``savReaderWriter`` now uses version 21.0.0.1 (i.e., Fixpack 1) of the I/O module.

Optional features
-------------------

**cWriterow.**
The ``cWriterow`` package is a faster Cython implementation of the pyWriterow method (66 % faster). To install it, you need Cython and run ``setup.py`` in the ``cWriterow`` folder::

    easy_install cython
    python setup.py build_ext --inplace

**numpy.**

* The ``numpy`` package should be installed if you intend to use array slicing (e.g ``data[:2,2:4]``).
* ``numpy`` is also needed to use the ``SavReaderNp`` sav-to-numpy class

Enviroment variables
---------------------
**SAVRW_DISPLAY_WARNS.** To issue warnings you can set an enviroment variable ``SAVRW_DISPLAY_WARNS`` to any of the following actions: "error", "ignore", "always", "default", "module", "once". If the enviroment variable is not defined, warnings are ignored. Note that warnings are usually harmless, e.g. ``SPSS_NO_LABELS``. See: http://docs.python.org/2/library/warnings.html. 

**SAVRW_USE_CWRITEROW.** You can use this variable to toggle between the ``cWriterow`` and the ``pyWriterow`` method, by setting this variable to ``ON`` or ``OFF``, respectively. This is intended for testing purposes.

**DYLD_LIBRARY_PATH.** Users of Mac OSX need to set this variable, see elsewhere in this documentation.

Typical use (the TLDR version)
------------------------------

The full documentation can be found in the :ref:`generated-api-documentation`.
Here are the most important parts::
    
    # ---- reading files    
    with SavReader('someFile.sav', returnHeader=True) as reader:
        header = next(reader)
        for line in reader:
            process(line)

    # ---- writing files    
    savFileName = 'someFile.sav'
    records = [[b'Test1', 1, 1], [b'Test2', 2, 1]]
    varNames = ['var1', 'v2', 'v3']
    varTypes = {'var1': 5, 'v2': 0, 'v3': 0}
    with SavWriter(savFileName, varNames, varTypes) as writer:
        for record in records:
            writer.writerow(record)

    # ---- reading file metadata
    with SavHeaderReader(savFileName) as header:
        metadata = header.dataDictionary(True)
        report = str(header)
        print(report)

    # ---- reading into numpy arrays
    reader_np = SavReaderNp('Employee data.sav")
    array = reader_np.to_structured_array()
    mean_salary = array["salary"].mean()
    reader_np.close()

    # ---- reading a file in unicode mode (default in SPSS v21 and up)
    >>> with SavReader('greetings.sav', ioUtf8=True) as reader:
    ...    for record in reader:
    ...        print(record[-1])
         নমস্কাৰ
         আসসালামুআলাইকুম     
    Greetings and salutations                         
    გამარჯობა                       
    Сәлеметсіз бе                         
    Здравствуйте                          
    ¡Hola!                                           
    Grüezi                                           
    สวัสดี                                
    Bondjoû  

    # ---- reading a file in codepage mode
    # wrong: variables with accented characters are returned as v1, v2, v3
    >>> with SavHeaderReader('german.sav') as header:
    ...     print(header.varNames)
    [b'python', b'programmieren', b'macht', b'v1', b'v2', b'v3']

    # correct: variable names contain non-ascii characters
    # locale definition and presence is OS-specific
    # Linux: sudo localedef -f CP1252 -i de_DE /usr/lib/locale/de_DE.cp1252
    >>> with SavHeaderReader('german.sav', ioLocale='de_DE.cp1252') as header:
    ...     print(header.varNames)
    [b'python', b'programmieren', b'macht', b'\xfcberhaupt', b'v\xf6llig', b'spa\xdf']

.. warning::

   The program calls ``spssFree*`` C functions to free memory allocated to dynamic arrays. This previously sometimes caused segmentation faults. This problem now appears to be solved. However, if you do experience segmentation faults you can set ``segfaults=True`` in ``__init__.py``. This will prevent the spssFree* functions from being called (and introduce a memory leak).


.. _formats:

Formats
----------

SPSS knows just two different data types: string and numerical data. These data types can be *formatted* (displayed) by SPSS in several different ways. Format names are followed by total width (w) and an optional number of decimal positions (d). **Table 1** below shows a complete list of all the available formats.

**String** data can be alphanumeric characters (``A`` format) or the hexadecimal representation of alphanumeric characters (``AHEX`` format). The maximum size of a string value is 32767 bytes. String formats do not have any decimal positions (d). Currently, ``SavReader`` maps both of the string formats to a regular alphanumeric string format. 

**Numerical** data formats include the default numeric format (``F``), scientific notation (``E``) and zero-padded (``N``). For example, a format of ``F5.2`` represents a numeric value with a total width of 5, including two decimal positions and a decimal indicator. For all numeric formats, the maximum width (w) is 40. For numeric formats where decimals are allowed, the maximum number of decimals (d) is 16. ``SavReader`` does not format numerical values, except for the ``N`` format, and dates/times (see under `Date formats`_). The ``N`` format is a zero-padded value (e.g. SPSS format ``N8`` is formatted as Python format ``%08d``, e.g. '00001234'). For most numerical values, formatting means *loss of precision*. For instance, formatting SPSS ``F5.3`` to Python ``%5.3f`` means that only the first three digits are retained. In addition, formatting incurs *additional processing time*. Finally, e.g. appending a percent sign to a value (``PCT`` format) renders the value *less useful for calculations*.

.. exceltable:: **Table 1.** string and numerical formats in SPSS and ``savReaderWriter`` 
   :file: ./formats.xls
   :header: 1
   :selection: A1:D19

*Note.* The User Programmable currency formats (CCA, CCB, CCC and CCD) cannot be defined or written by ``SavWriter`` and existing definitions cannot be read by ``SavReader``.

.. _dateformats:

Date formats
-------------
**Dates in SPSS.** Date formats are a group of numerical formats. SPSS stores dates as the number of seconds since midnight, October 14, 1582 (the beginning of the Gregorian calendar). In SPSS, the user can make these seconds human-readable by giving them a print and/or write format (usually these are set at the same time using the ``FORMATS`` command). Examples of such display formats include ``ADATE`` (American date, *mmddyyyy*) and ``EDATE`` (European date, *ddmmyyyy*), ``SDATE`` (Asian/Sortable date, *yyyymmdd*) and ``JDATE`` (Julian date). 

**Reading dates.** ``SavReader`` deliberately does *not* honor the different SPSS date display formats, but instead tries to convert them to the more practical (sortable) and less ambiguous ISO 8601 format (*yyyy-mm-dd*). You can easily change this behavior by modifying the ``supportedDates`` dictionary in ``__init__.py``. **Table 2** below shows how ``SavReader`` converts SPSS dates. Where applicable, the SPSS-to-Python conversion always results in the 'long' version of a date/time. For instance, ``TIME5`` and ``TIME40.16`` both result in a ``%H:%M:%S.%f``-style format. If you do not want ``SavReader`` to automatically convert dates, you can set ``rawMode=True``. If you use this setting, keep in mind that ``SavReader`` will also not convert system missing values (``$SYSMIS``) to an empty string; instead sysmis values will appear as the smallest value that can be represented on that system (``-1 * sys.float_info.max``)

.. exceltable:: **Table 2.** Date formats in SPSS and ``SavReader`` 
   :file: ./dates.xls
   :header: 1
   :selection: A1:I25

*Note.*
[1] `IBM SPSS Statistics Command Syntax Reference.pdf`_
[2] http://docs.python.org/2/library/datetime.html
[3] ISO 8601 format dates are used wherever possible, e.g. mmddyyyy (``ADATE``) and ddmmyyyy (``EDATE``) is not maintained.
[4] Months are converted to quarters using a simple lookup table
[5] weekday, month names depend on host locale (not on ``ioLocale`` argument)

**Writing dates.** With ``SavWriter`` a Python date string value (e.g. "2010-10-25") can be converted to an SPSS Gregorian date (i.e., just a whole bunch of seconds) by using the ``spssDateTime`` method, e.g.::

    kwargs = dict(savFileName='/tmp/date.sav', varNames=['aDate'], 
                  varTypes={'aDate': 0}, formats={'aDate': 'EDATE40'})
    with SavWriter(**kwargs) as writer:
        spssDateValue = writer.spssDateTime(b'2010-10-25', '%Y-%m-%d')
        writer.writerow([spssDateValue])

The display format of the date (i.e., the way it looks in the SPSS data editor after opening the .sav file) may be set by specifying the ``formats`` dictionary (see also **Table 1**). This is one of the optional arguments of the ``SavWriter`` initializer. Without such a specification, the date will look like a large integer (the number of seconds since the beginning of the Gregorian calendar).

Indices and tables
==================

.. toctree::
   generated_api_documentation.rst
   :maxdepth: 2

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

