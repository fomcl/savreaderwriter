import sys
sys.path.append("/home/antonia/Desktop/savReaderWriter")
from savReaderWriter import *
import os
from ctypes import *
#print os.path.abspath("./spssio/win32/spssio32.dll")
#print WinDLL(os.path.abspath("./spssio/win32/spssio32.dll"))
xxx

##if sys.platform.startswith("win"):
##    os.chdir("d:/temp/spssio")
##else:
##    os.chdir("/media/Media/temp/spssio")
#os.chdir(os.path.abspath("."))
savFileName = "spssio_test.sav"
#savFileName = "employee data.sav"
#savFileName = "mrsets.sav"
#savFileName = "test_wholeDict.sav"
import random
import glob
with SavHeaderReader(savFileName) as h:
    print unicode(h)

xxx
h = Header(savFileName, mode="rb", refSavFileName=None,
           ioUtf8=False, ioLocale=None)
items = ["alignments", "valueLabels", "varSets", "varAttributes",
         "fileAttributes", "multRespDefs", "dateVariables"]
for item in items:
    print getattr(h, item)
    
#print h.valueLabels
#print h.varNames
xxx
d = {}
savFileNames = glob.glob(r"D:\temp\spssio\sample\*.sav")
#(8, 'D:\\temp\\spssio\\sample\\voter.sav'),
#(10, 'D:\\temp\\spssio\\sample\\World 95 for Missing Values.sav'),
savFileNames = \
[(6, 'D:\\temp\\spssio\\sample\\Trends chapter 5.sav'),
 (6, 'D:\\temp\\spssio\\sample\\Inventor.sav'),
 (7, 'D:\\temp\\spssio\\sample\\screws.sav'),
 (7, 'D:\\temp\spssio\\sample\\guttman.sav'),
 (8, 'D:\\temp\\spssio\\sample\\tv-survey.sav'),
 (9, 'D:\\temp\\spssio\\sample\\map_data.sav'),
 (11, 'D:\\temp\\spssio\\sample\\World95.sav'),
 (14, 'D:\\temp\\spssio\\sample\\Predefined Validation Rules SPSS 14.0.sav'),
 (19, 'D:\\temp\\spssio\\sample\\Merry_Christmas_and_Happy_New_Year.sav'),
 (21, 'D:\\temp\\spssio\\sample\\another_test.zsav')]
##
##for savFileName in savFileNames[::-1]:
##    version, savFileName = savFileName
##    print os.path.basename(savFileName), version
##    h = Header(savFileName, mode="rb", refSavFileName=None,
##               ioUtf8=False, ioLocale=None)
##    d[savFileName] = h.spssVersion
##print d
##
##categorical  = {"setType": "C", "label": "labelC",
##               "varNames": ["salary", "educ"]}
##dichotomous1 = {"setType": "D", "label": "labelD",
##                "varNames": ["salary", "educ"], "countedValue": "Yes"}
##dichotomous2 = {"setType": "D", "label": "", "varNames":
##                ["salary", "educ", "jobcat"], "countedValue": "No"}
##extended1    = {"setType": "E", "label": "", "varNames": ["bdate",
##                "salary", "educ"], "countedValue": "1",
##                "firstVarIsLabel": True}
##multRespDefs = {"testSetC": categorical, "testSetD1": dichotomous1,
##                "testSetD2": dichotomous2, "testSetEx1": extended1}


items = ["alignments", "valueLabels", "varSets", "varAttributes",
         "fileAttributes", "multRespDefs", "dateVariables"]
items = [items[1]]
random.shuffle(savFileNames)
for savFileName in savFileNames:
    version, savFileName = savFileName
    print ("%s - %s" % (version, savFileName)).center(79, "*")
    gc.collect()
    h = Header(savFileName, mode="rb", refSavFileName=None,
               ioUtf8=False, ioLocale=None)
    for i in range(1):
    #for i, prop in enumerate(items):
        #print h.spssVersion
        #print h.multRespDefs 
        prop = random.choice(items)
        print "----", i, prop, "-----"
        try:
            getattr(h, prop)
        except SPSSIOError, e:
            print e
    h.closeSavFile(h.fh, mode="rb")
    time.sleep(0.5)
    #h.closeFile()
