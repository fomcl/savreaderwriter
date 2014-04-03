
cdef pad_string(char* s, int width):
     cdef int padding
     padding = -8 * (width // -8)
     return s + (padding - len(s)) * b' '

def cWriterow(self, record):
    """ This function writes one record, which is a Python list,
    Faster implementation of the _pyWriterow method."""
    cdef int varType
    cdef Py_ssize_t i
    float_ = float
    for i, value in enumerate(record):
        varName = self.varNames[i]
        varType = self.varTypes[varName]
        if varType == 0:
            try:
                value = float_(value)
            except (ValueError, TypeError):
                value = self.sysmis_
        else:
            #value = self.pad_string(value, varType)
            value = pad_string(value, varType)
            #if self.ioUtf8_ and varType:
            if self.ioUtf8_ and isinstance(value, unicode):
                value = value.encode("utf-8")
        record[i] = value
    self.record = record