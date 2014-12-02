#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
import abc
import sys
import os
import mmap
import re
import locale
import threading
import time
from collections import namedtuple as ntuple
from random import randint
from ctypes import c_int, c_long

from PyQt4.QtCore import *
from PyQt4.QtGui import *


"""
savViewer - SPSS Data file viewer

Currently supported are:
-SPSS Data file (.sav, .zsav)  -- depends on savReaderWriter
-Character separated values (.csv, .tab) -- depends on icu (and csv)
-Microsoft Excel (*.xls, *.xlsx) -- depends on xlrd

Commandline use: python savViewer.py somefile.sav
GUI use: python savViewer.py 

Suitable for use with Python 2.7 and 3.3
"""

__author__ = "Albert-Jan Roskam"
__email__ = "@".join(["fomcl", "yahoo." + "com"])
__version__ = "1.0.3"
__date__ = "2014-11-18"


# Python 3

py3k = sys.version_info.major >= 3

try:
   from itertools import izip_longest
except ImportError:
   from itertools import zip_longest as izip_longest

try:
    xrange
except NameError:
    xrange = range

try:
    unicode
except NameError:
    unicode = str

# ensure locale.getlocale won't return (None, None)
locale.setlocale(locale.LC_ALL, "")  

class ExtIterBase(object):

    """
    Abstract base class that should make it easier to add concrete 
    *Iter (e.g. SavIter, CsvIter) classes
    """ 

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError("need __iter__ method")

    @abc.abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError("need __getitem__ method")

    @abc.abstractmethod
    def close(self):
        """Does some cleanup, if needed"""
        raise NotImplementedError("need close method")

    @abc.abstractproperty
    def fileEncoding(self):
        """Returns the encoding of a dataset"""
        return NotImplementedError("need fileEncoding property")

    @abc.abstractproperty
    def shape(self):
        """Returns the shape of a dataset as a namedtuple with nrows, ncols"""
        return NotImplementedError("need shape property")

    @abc.abstractproperty
    def varNames(self):
        """Returns the variable names of a dataset as a list"""
        return NotImplementedError("need varNames property")


class CsvIter(ExtIterBase):

    def __init__(self, csvFileName):
    
        global csv, codecs, icu 
        import csv 
        import codecs
        import cStringIO
        try:
            import icu  # sudo apt-get install libicu && pip install pyicu
            self.icuOk = True
        except ImportError:
            self.icuOk = False

        self.csvFileName = csvFileName

        self.fileSize = os.path.getsize(self.csvFileName)
        self.sampleSize = 2048 if self.fileSize > 2048 else self.fileSize
        self.fileEncoding_ = self._get_encoding(self.csvFileName)

        self.csvfile = codecs.open(self.csvFileName, "r+", self.fileEncoding)
        self.data = self.mapfile(self.csvfile)
        self.dialect = self._get_dialect(self.csvFileName, self.fileEncoding)
        self.varNames_ = self._get_header(self.csvFileName, 
                                          self.fileEncoding, 
                                          self.dialect)
        self.Shape = ntuple("Shape", ["nrows", "ncols"])

        self.lookup = list()
        self.lookup_done = False
        self.thread = threading.Thread(target=self._get_row_lookup,
                                       args=(open(self.csvFileName, "rb"),),
                                       name="lookup maker thread")
        self.thread.start()

    def __iter__(self):
        args = (self.csvfile, self.dialect, self.fileEncoding)
        return self.unicode_csv_reader(*args)

    def __getitem__(self, key):
        """return an item from a memory-mapped csv file"""
        try:
            start = self.lookup[key]
            end = self.lookup[key + 1]
        except IndexError:
            end = self.fileSize
            if self.thread.is_alive():
                print("One moment please, lookup not yet ready enough")
            elif abs(key) >= len(self.lookup):
                raise IndexError("index out of range")
        finally:
            if self.lookup_done:
                self.thread.join()

        if py3k:  
            # 3.x csv requires unicode
            line = self.data[start:end].strip().decode(self.fileEncoding_)
            return next(csv.reader(line, dialect=self.dialect))
        else:
            # 2.x csv lacks unicode support
            line = self.data[start:end].strip()
            row = next(csv.reader([line], dialect=self.dialect))
            return [cell.decode(self.fileEncoding_) for cell in row]

    def mapfile(self, fileObj):
        size = os.path.getsize(fileObj.name)
        return mmap.mmap(fileObj.fileno(), size)

    def _get_row_lookup(self, fObj):
        record_start = 0
        for line in fObj:
            if not line:
                break
            self.lookup.append(record_start)
            # len(), because fObj.tell() --> won't work with threading
            record_start += len(line)  
        self.lookup_done = True

    def close(self):
        self.csvfile.close()

    @property
    def fileEncoding(self):
        return self.fileEncoding_

    def _get_encoding(self, csvFileName):
        if not self.icuOk:
            return locale.getpreferredencoding()
        with open(csvFileName) as csvfile:
            sample = csvfile.read(self.sampleSize)
        cd = icu.CharsetDetector()
        cd.setText(sample)
        encoding = cd.detect().getName()
        return encoding

    def _get_dialect(self, csvFileName, encoding):
        try:
            csvfile = codecs.open(csvFileName, encoding=encoding)
            sample = csvfile.read(self.sampleSize).encode(encoding)
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
        except csv.Error:
            print("NOTE. Can't guess csv dialect. Assuming excel dialect")
            dialect = csv.excel
        finally:
            csvfile.close()
        return dialect

    @property
    def varNames(self):
        return self.varNames_

    def _get_header(self, csvFileName, encoding, dialect):
        try:
            csvfile = codecs.open(csvFileName, encoding=encoding)
            sample = csvfile.read(self.sampleSize).encode(encoding)
            has_header = csv.Sniffer().has_header(sample)
        except csv.Error:
            has_header = False
        finally:
            csvfile.seek(0)
            data = csv.reader(csvfile, dialect)
            varNames = next(data)
            if not has_header:
                varNames = ["col_%04d" % i for i in range(len(varNames))]
            csvfile.close()
        return varNames

    @property
    def shape(self):
        nrows = 25 if not self.lookup else len(self.lookup)
        ncols = len(self.varNames)
        return self.Shape(nrows, ncols)

    # source: https://docs.python.org/2/library/csv.html (bottom of page)
    def unicode_csv_reader(self, unicode_csv_data, dialect, encoding, **kwargs):
        csv_reader = csv.reader(self.utf_8_encoder(unicode_csv_data, encoding),
                                dialect=dialect, **kwargs)
        for row in csv_reader:
            yield [unicode(cell, encoding) for cell in row]

    def utf_8_encoder(self, unicode_csv_data, encoding):
        for line in unicode_csv_data:
            yield line.encode(encoding)

TabIter = CsvIter


class XlsIter(ExtIterBase):

    def __init__(self, xlsFileName):
    
        global xlrd
        import xlrd

        self.xlsFileName = xlsFileName
        self.file = open(self.xlsFileName, "rb")
        self.xlsfile = xlrd.open_workbook(file_contents=mmap.mmap(
                                          self.file.fileno(), 0, 
                                          access=mmap.ACCESS_READ))
        self.shape_ = self._get_shape(self.xlsfile)
        self.varNames_ = self._get_header(self.shape.ncols)
        self.lookup = self._get_row_lookup()

    def __iter__(self):
        sheet_names = self.xlsfile.sheet_names()
        for sheet_name, sheet in zip(sheet_names, self.xlsfile.sheets()):
            for row in range(sheet.nrows):
                record = [sheet_name]
                for col in range(sheet.ncols):
                    value = sheet.cell(row, col).value
                    record.append(value)
                yield record 

    @property
    def fileEncoding(self):
        return "utf-8"

    @property
    def shape(self):
        return self.shape_

    @property
    def varNames(self):
        return self.varNames_

    def _get_row_lookup(self):
        lookup, global_row = {}, 0
        for sheetno, sheet in enumerate(self.xlsfile.sheets()):
            for local_row in xrange(sheet.nrows):
                lookup[global_row] = (sheetno, local_row)
                global_row += 1
        return lookup

    def __getitem__(self, key):
        try:
            sheetno, local_row = self.lookup[key]
        except KeyError:
            raise IndexError("index out of range")
        sheet_name = [self.xlsfile.sheet_names()[sheetno]]
        record = self.xlsfile.sheets()[sheetno].row_values(local_row)
        return sheet_name + record

    def close(self):
        self.file.close()

    def _get_shape(self, xlsfile):
        nrows, ncols = [], []
        for sheet in self.xlsfile.sheets():
            nrows.append(sheet.nrows) 
            for row in xrange(sheet.nrows):
                ncols.append(sheet.ncols + 1) # + 1 for the sheetname itself
        nrows, ncols = sum(nrows), max(ncols)
        return ntuple("Shape", ["nrows", "ncols"])(nrows, ncols)

    def _get_header(self, ncols):
        return ["col_%04d" % i for i in range(ncols)]

XlsxIter = XlsIter


class SavIter(ExtIterBase):

    def __init__(self, savFileName):

        global SavReader, locale
        from savReaderWriter import SavReader

        self.savFileName = savFileName
        self.records = self.data(self.savFileName)
        #self.init_seekNextCase()

    def __iter__(self):
        return self.records.__iter__()

    def __getitem__(self, key):
        # TODO: use spssSeekNextCase here!
        #self.seekNextCase(self.fh, key)
        #return self.records.record 
        return self.records.__getitem__(key)

    def init_seekNextCase(self):
        self.spssio = self.records.spssio
        self.fh = self.records.fh
        self.seekNextCase = self.spssio.spssSeekNextCase
        self.seekNextCase.argtypes = [c_int, c_long]
        retcode = self.seekNextCase(self.fh, self.shape.nrows)
        #if retcode:
        #    raise SPSSIOError("error seeking case", retcode)  

    def close(self):
        return self.records.close()

    @property
    def fileEncoding(self):
        return self.records.fileEncoding

    @property
    def shape(self):
        return self.records.shape

    @property
    def varNames(self):
        decode = lambda x: unicode(x, self.fileEncoding)
        try:
            return list(map(decode, self.records.varNames))
        except TypeError:
            return self.records.varNames  # ioUtf8=True

    def data(self, savFileName):
        kwargs = dict(savFileName=savFileName, ioUtf8=True, recodeSysmisTo=float("nan"))
        data = SavReader(**kwargs)
        if not data.isCompatibleEncoding():
            del kwargs["ioUtf8"]
            encoding = data.fileEncoding.replace("_", "-")
            encoding = re.sub(r"cp(\d+)", r"\1", encoding)
            locale_ = locale.getlocale()[0] + "." + encoding
            kwargs["ioLocale"] = locale_
            data.close()
            try:
                data = SavReader(**kwargs)
            except ValueError:
                msg = ("Locale not found --> Linux: sudo localedef -f "
                       "%s -i %s /usr/lib/locale/%s")
                msg = msg % (encoding.upper(), locale_.split(".")[0], locale_) 
                raise ValueError(msg)
        return data

ZsavIter = SavIter


##################
class Menu(QMainWindow):

    def __init__(self, app):
        super(Menu, self).__init__()
        self.app = app
        self.setWindowTitle("Welcome to Data File Viewer!")
        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.setCentralWidget(self.main_widget)
        self.statusBar()
        self.create_spinbox_group()

        self.table = Table(savFileName=None)
        self.main_layout.addWidget(self.table)

        self.createActions()
        self.create_menu_bar()
        self.main_widget.setLayout(self.main_layout)
        self.show()
        self.set_filename()

        self.start_thread()
        self.update_screen()

    def create_menu_bar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openFile)  
        fileMenu.addAction(self.exitAct)  
        aboutMenu = menubar.addAction(self.aboutAct)

    def set_filename(self):
        if len(sys.argv) == 2:  # commandline use
            self.table.savFileName = os.path.abspath(os.path.expanduser(sys.argv[1]))
        else:
            self.showDialog()
        self.read_file()

    def read_file(self):
        if self.table.savFileName:
            self.table.records = self.table.data(self.table.savFileName)
            nrows, ncols = self.table.records.shape 
            self.spin_box.setRange(-nrows - 1, nrows - 1)
            self.table.create_vert_scrollbar(nrows)  # redraw
            self.table.create_table(self.table.block_size, self.table.records.varNames)
            self.table.update_grid()
            nrows, ncols = "{:,}".format(nrows), "{:,}".format(ncols)
            self.table.title = "%s (%s rows, %s columns)" % (self.table.savFileName, nrows, ncols)
            self.setWindowTitle(self.table.title)

    def showDialog(self):
        if hasattr(self.table, "records"):
            self.table.records.close()

        # in case of a previously opened file: start in same directory
        if self.table.savFileName:
            directory = os.path.dirname(self.table.savFileName)
        else:
            directory = os.path.expanduser("~")
        selectedFilter = ("SPSS Data files (*.sav *.zsav);;"
                          "Character-Separated Values files (*.csv *.tab);;"
                          "Excel files (*.xls *.xlsx);;"
                          "All Files (*)")
        args = ('Open file', directory, selectedFilter) 
        self.table.savFileName = QFileDialog.getOpenFileName(self, *args)
        if not py3k: 
            fs_encoding = sys.getfilesystemencoding()  # windows okay? mbcs??
            self.table.savFileName = unicode(self.table.savFileName, fs_encoding)
        self.read_file()

    def create_spinbox_group(self):
        group = QGroupBox()    
        group.setTitle("Retrieve record")
        self.main_layout.addWidget(group)

        hbox = QHBoxLayout()
        hbox.setSpacing(0)

        # initialize spinbox with some defaults
        self.spin_box = QSpinBox(self)
        self.spin_box.setRange(-100, 100)
        self.spin_box.setSingleStep(1)
        self.spin_box.setPrefix("# ")
        self.spin_box.setSpecialValueText("invalid")
        hbox.addWidget(self.spin_box)

        go_button = QPushButton('Go to record', self)
        tooltip = "Enter an integer (0 = first record, -1 = last record)"
        go_button.setToolTip(tooltip)
        hbox.addWidget(go_button)

        # add a checkbox -for fun
        cb = QCheckBox('Managerize data', self)
        def do_cb():
            self.table.do_managerize = cb.isChecked() 
        QObject.connect(cb, SIGNAL("stateChanged(int)"), do_cb)
        hbox.addWidget(cb)

        group.setLayout(hbox)
        hbox.addStretch(1) 

        def retrieve():
            if hasattr(self.table, "records"):
                value = self.spin_box.value()
                value = self.table.records.shape.nrows + value if value < 0 else value
                self.table.populate_table(self.table.records, value)
                self.table.vert_scroll.setValue(value) # synchronize scroll & spinbox
        QObject.connect(go_button, SIGNAL("clicked()"), retrieve)

    def createActions(self):
        self.openFile = QAction(QIcon('open.png'), 'Open', self)
        self.openFile.setShortcut('Ctrl+O')
        self.openFile.setStatusTip('Open new File')
        self.connect(self.openFile, SIGNAL("triggered()"), self.showDialog)

        self.exitAct = QAction(self.tr("&Exit"), self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(self.tr("Exit the application"))
        self.connect(self.exitAct, SIGNAL("triggered()"), self, SLOT("close()"))

        self.aboutAct = QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        self.connect(self.aboutAct, SIGNAL("triggered()"), self.about)

    def about(self):
        title = "SPSS Data File Viewer\n\n%s\n(%s)\nversion %s\n%s"
        title = title % (__author__, __email__, __version__, __date__) 
        QMessageBox.about(self, self.tr("About"), self.tr(title))

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def start_thread(self):
        self.thread = QThread() 
        self.connect(self.thread , SIGNAL('update(QString)') , self.update_screen)
        self.thread.start()

    def update_screen(self):
        previous_nrows = -1
        while True:
            nrows, ncols = self.table.records.shape
            title = "{} ({:,} rows, {:,} columns)"
            title = title.format(self.table.savFileName, nrows, ncols)
            self.setWindowTitle(title)
            self.table.vert_scroll.setRange(0, nrows - 1) 
            self.spin_box.setRange(-nrows, nrows)
            self.app.processEvents()
            time.sleep(0.05)
            if previous_nrows >= nrows:
                break 
            previous_nrows = nrows

class MyScrollBar(QScrollBar):
    """vertical scroll bar of grid"""
    def mouseReleaseEvent(self, event):
        self.emit(SIGNAL("clicked()"))

class Table(QDialog):

    """
    Read a supported data file blockwise, with <block_size> records at a time,
    display in a table grid
    """

    def __init__(self, savFileName, block_size=25, parent=None):
        super(Table, self).__init__(parent)
        self.savFileName = savFileName
        self.block_size = block_size
        self.layout = QGridLayout()
        self.setLayout(self.layout) 
        self.create_table(self.block_size)
        self.create_vert_scrollbar()
        self.update_grid() 
        self.do_managerize = False  # :-)

    def data(self, fileName):
        extension = os.path.splitext(fileName)[1]
        classname = extension[1:].title() + "Iter"
        try: 
            return globals()[classname](fileName)
        except KeyError:
            raise TypeError("Unknown filetype: %r" % extension)

    def create_vert_scrollbar(self, upper=100):
        self.vert_scroll = MyScrollBar(Qt.Vertical, self.table)
        self.vert_scroll.setSingleStep(1)
        self.vert_scroll.setFocusPolicy(Qt.StrongFocus)
        self.vert_scroll.setValue(0)
        self.vert_scroll.setRange(0, upper - 1) 
        self.layout.addWidget(self.vert_scroll, 0, 1)
        QObject.connect(self.vert_scroll, SIGNAL("clicked()"), self.update_grid)

    def create_table(self, block_size, colnames=None):
        if colnames: 
            self.table = QTableWidget(block_size, len(colnames))
            self.table.setHorizontalHeaderLabels(colnames)
        else:  # initialize empty table
            self.table = QTableWidget(block_size, block_size)
            self.table.setHorizontalHeaderLabels([""] * block_size)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setAlternatingRowColors(True)
        self.layout.addWidget(self.table, 0, 0)
        self.table.resizeRowsToContents()

    def update_grid(self):
        if not self.savFileName:
            return   # initialize empty table
        slider_value = self.vert_scroll.value()
        percentage = slider_value / self.records.shape.nrows * 100
        tooltip = "record # %d (%2.1f %%)" % (slider_value, percentage)
        self.vert_scroll.setToolTip(tooltip)
        self.populate_table(self.records, slider_value)

    def populate_table(self, data, start_row=None):

        dim = data.shape
        encoding = data.fileEncoding
        varNames = data.varNames
        
        # get block numbers
        start_row = self.vert_scroll.value() if start_row is None else start_row
        end_row = start_row + self.block_size
        end_row = dim.nrows if end_row > dim.nrows else end_row
        block = range(start_row, end_row)
        fake_block = range(self.block_size)

        # redraw a smaller grid, if needed
        if len(block) != self.block_size:
            self.create_table(len(block), varNames)
        else:
            self.create_table(self.block_size, varNames)

        # set row/column labels
        if py3k:        
            self.table.setVerticalHeaderLabels(list(map(str, block)))
        else:
            self.table.setVerticalHeaderLabels(QStringList(map(str, block)))
        self.table.setHorizontalHeaderLabels(varNames)

        # fill the grid with values. The very last block is annoying
        for row, fake_row in izip_longest(block, fake_block):
            row_exists = row is not None
            if row_exists:
                record = data[row]
            for col in range(dim.ncols):
                 if row_exists:
                    try:
                        value = self._convert(record[col], encoding)
                    except IndexError:
                        value = ""  # could be needed for multisheet xls files
                    except TypeError:
                        break
                        #value = "<???>"
                    table_item = QTableWidgetItem(value)
                    if value == u"nan":
                        table_item.setTextColor(QColor("red"))
                        table_item.setBackgroundColor(QColor("yellow"))
                    elif value == u"":
                        table_item.setBackgroundColor(QColor("gray"))

                    if self.do_managerize:
                        table_item.setBackgroundColor(QColor(self.managerize())) 
                    self.table.setItem(fake_row, col, table_item)
                    #self.table.setItem(fake_row, col, QTableWidgetItem(value))
            if not row_exists: 
                break 

    def _convert(self, value, encoding):
        try:
            return unicode(value, encoding)
        except TypeError:
            return unicode(value)

    def managerize(self):
        rgb = (randint(0, 255), randint(0, 255), randint(0, 255))
        return '#%02x%02x%02x' % rgb

if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = Menu(app)
    screen = QDesktopWidget().screenGeometry()
    menu.resize(screen.width(), screen.height())
    sys.exit(app.exec_())
