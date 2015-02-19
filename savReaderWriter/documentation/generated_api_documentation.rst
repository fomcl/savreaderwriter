.. _generated-api-documentation:

Generated API documentation
===========================

.. autosummary::
   :toctree: DIRNAME

SavReader
---------
.. autoclass:: savReaderWriter.SavReader
   :member-order: bysource
   :members:
   :special-members:
   :show-inheritance:

SavReaderNp
-----------

.. versionadded:: 3.4.0

.. autoclass:: savReaderWriter.SavReaderNp
   :member-order: bysource
   :members:
   :special-members:
   :show-inheritance:

SavHeaderReader
---------------
.. autoclass:: savReaderWriter.SavHeaderReader
   :member-order: bysource
   :members:
   :special-members:
   :show-inheritance:

SavWriter
---------

The most commonly used metadata aspects include `VARIABLE LABELS`, `VALUE LABELS`, `FORMATS` and `MISSING VALUES`.
 
.. autoclass:: savReaderWriter.SavWriter
   :member-order: bysource
   :members:
   :special-members:
   :show-inheritance:


Header
------

.. note::
   This class should not be used directly. Use ``SavHeaderReader`` or ``SavReader`` to retrieve metadata.

.. autoclass:: savReaderWriter.Header
   :member-order: bysource
   :members: numberofCases, numberofVariables, varNamesTypes, valueLabels, varLabels, formats, missingValues, measureLevels, columnWidths, alignments, varSets, varRoles, varAttributes, fileAttributes, multRespDefs, caseWeightVar, textInfo, fileLabel
   :show-inheritance:

Generic
-------

.. note::
   This class should not be used directly

.. autoclass:: savReaderWriter.Generic
   :member-order: bysource
   :members: byteorder, spssVersion, spssioVersion, fileCompression, systemString, sysmis, ioLocale, missingValuesLowHigh, fileCodePage, isCompatibleEncoding, ioUtf8, fileEncoding
   :special-members:
   :show-inheritance:

