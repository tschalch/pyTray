"""
TrayFileHandler Class for XML file handling. Opens and saves
xml files and provides the xml DOM to the tray data classes.
Chooses the right xml DOM class based on the file version
"""

# debugging with winpdb:
#import rpdb2
#rpdb2.start_embedded_debugger("test")

import zipfile

# import both modules, since cElementTree depends on elementtree
#import xml.etree.ElementTree
import xml.etree.cElementTree as ET

from PIL import Image
#Image._initialized=2
import cStringIO
import os, os.path, random, shutil
from util.trayErrors import NoZipFileError
from elmtree_tray_item import TrayItem
from elmtree_jtray import JTrayData
import tray_data

expFilename = "Experiment.xml"
thumbsize = (250,194)

class XMLBackend:
    def __init__(self, screenFilename, defFilename, UserData, newScreen = None):
        self.xmlFile = XMLFileHandler(screenFilename, UserData, newScreen)
        self.defFile = XMLFileHandler(defFilename)
        self.tree = self.xmlFile.tree
        self.rootElement = self.xmlFile.root
        self.defElement = self.defFile.root

    def Close(self):
        self.xmlFile.tempzip.close()
        
    def GetFilename(self):
        return self.xmlFile.filename
        
    def AddImage(self, image, imageName):
        return self.xmlFile.AddImage(image, imageName)

    def GetChildren(self, trayItem, ChildName):
        kids = []
        definition = self.defElement.find(ChildName)
        for k in trayItem.element.findall(ChildName):
            kids.append(TrayItem(k, definition, trayItem))
        return kids
            
    def GetImage(self, imageName):
        return self.xmlFile.GetImage(imageName)

    def GetItems(self, elementName):
        definition = self.defElement.find(elementName)
        elements = self.rootElement.findall(elementName)
        trayItems = []
        for element in elements: 
            trayItems.append(TrayItem(element, definition, self.GetRoot()))
        return trayItems

    def GetNewItem(self, elementName, parentItem):
        definition = self.defElement.find(elementName)
        newElement = ET.XML(ET.tostring(definition, "utf-8"))
        for element in newElement.getiterator():
        	element.text = None
        return TrayItem(newElement, definition, parentItem)

    def GetParent(self, child):
        # Generate a mapping of parent to their children
        parent_map = dict((c, p) for p in self.tree.getiterator() for c in p)
        return parent_map[child.element]
    
    def GetVersion(self):
        try:
            return self.rootElement.attrib["Version"]
        except KeyError:
            return None
    
    def GetRoot(self):
        return TrayItem(self.rootElement, self.defElement)

    def OpenImage(self, imageName):
        self.xmlFile.OpenImage(imageName)

    def Print(self):
        print ET.tostring(self.rootElement, "utf-8")

    def Save(self, newFilename=None, saveAsZip = True):
        self.xmlFile.Save(newFilename, saveAsZip)
        

class XMLFileHandler:

    def __init__(self, filename, UserData=None, new=None):

        if filename:
            self.filename = os.path.abspath(filename)
        else:
            self.filename = None
        # initialize isZip, but leave it until first save to decide the file type
        self.isZip = True

        if new:
            self.tempfile = "%s/%i.exp~" % (UserData.GetTempDir()\
                            ,random.randint(0, 1000))
            self.NewScreen()
            return
        elif zipfile.is_zipfile(filename) and UserData:
            # setup temp file
            self.tempfile = "%s/%s%i.exp~" % (UserData.GetTempDir(),os.path.split(filename)[1]\
                            ,random.randint(0, 1000))
            self.StartTemp()
            self.ReadZip()
        elif zipfile.is_zipfile(filename):
            self.tempfile = "tempfile.zip"
            self.StartTemp()
            self.ReadZip()
            self.isZip = False
        else:
           self.ReadFile()

    def StartTemp(self):
        self.tempfile = os.path.abspath(self.tempfile)
        if self.filename and zipfile.is_zipfile(self.filename):
            shutil.copy(self.filename,self.tempfile)
            try:
              self.tempzip = zipfile.ZipFile(self.tempfile,"a")
            except IOError:
                print "Failed to open temp file ",self.tempfile,"."
                raise
        else:
            try:
              self.tempzip = zipfile.ZipFile(self.tempfile,"w")
            except IOError:
                print "Failed to setup temp file ",self.tempfile,"."
                raise
            
        
    
    def AddImage(self, image, imageName):
        zip = self.tempzip
        try:
            zip.namelist().index(imageName)
        except ValueError:
            imageFile = cStringIO.StringIO()
            image.save(imageFile, "jpeg", quality = 90)
            zip.writestr(str(imageName), imageFile.getvalue())
            # write thumbnail
            image.thumbnail(thumbsize, Image.ANTIALIAS)
            thumbFile = cStringIO.StringIO()
            image.save(thumbFile, "JPEG", quality = 90)
            zip.writestr("tb_" + str(imageName), thumbFile.getvalue())
            return 1
        return 0

    def CheckOutputDir(self):
        dirname = os.path.dirname(self.filename) + "/output"
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    def GetImage(self, imageName):
        imageName = str(imageName)
        try:
            #zip = zipfile.ZipFile(self.filename,"r")
            zip = self.tempzip
            imageFile = cStringIO.StringIO(zip.read(imageName))
        except IOError:
            print "Failed to open ",self.filename,"."
            raise
        return imageFile
        
    def NewScreen(self):
        self.root = ET.Element("Screen")
        self.tree = ET.ElementTree(self.root)
        self.root.attrib["Version"] = "1.0"
        self.StartTemp()

    def OpenImage(self, imageName):
        try:
            dirname = os.path.dirname(self.filename)
            self.CheckOutputDir()
            newFilename = os.path.normpath(dirname + "/output/" + "imageName" + ".jpg")
            f = file(newFilename, 'wb')
            f.write(self.GetImage(imageName).getvalue())
            f.close()
            os.startfile(f.name)
        except IOError:
            print "Failed to open ",self.filename,"."
            raise


    def ReadFile(self):
        try:
            self.tree = ET.parse(self.filename)
            self.root = self.tree.getroot()
        except IOError:
            print "Failed to open ",self.filename,"."
            raise
        except SyntaxError:
            print "The ",expFilename," file contains invalid XML code."
            raise
        
    def ReadZip(self):
        try:
            #zip = zipfile.ZipFile(self.filename,"r")
            zip = self.tempzip
            file = zip.read(expFilename)
            self.tree = ET.ElementTree(ET.XML(file))
            self.root = self.tree.getroot()
        except IOError:
            print "Failed to open ",self.filename,"."
            raise
        except SyntaxError:
            print "The ",expFilename," file contains invalid XML code."
            zip.close()
            raise
        # make thumbnails of images that don't have thumbs jet
        files = zip.namelist()
        for file in files:
            if not file.count(".xml") and not file.count(".jpg"):
                imageFile = cStringIO.StringIO(zip.read(file))
                # test if it is image
                try:
                    image = Image.open(imageFile)
                except IOError:
                    # is no image file
                    continue
                file = file + ".jpg"
                self.tempzip.writestr(str(file), imageFile.getvalue())
            if file.count(".jpg") and not file.count("tb_") \
                                  and not files.count("tb_"+file):
                imageFile = self.GetImage(file)
                image = Image.open(imageFile)
                image.thumbnail(thumbsize, Image.ANTIALIAS)
                thumbFile = cStringIO.StringIO()
                image.save(thumbFile, "JPEG", quality = 90)
                zip.writestr("tb_" + str(file), thumbFile.getvalue())

    def Save(self, newFilename=None, saveAsZip=True):
        if not saveAsZip or not self.isZip:
            if newFilename:
                self.filename = os.path.abspath(newFilename)
            self.isZip = False
            fout = open(self.filename,'w')
            fout.write(ET.tostring(self.root,"UTF-8"))
            fout.close
            return

        if (not self.filename and newFilename):
            self.filename = os.path.abspath(newFilename)
            zip = zipfile.ZipFile(self.filename,"w")
            zip.close()

        tempfile = os.path.abspath(self.filename + "~")
        if newFilename:
            shutil.copy(self.filename,tempfile)
            self.filename = newFilename
        else:
            os.rename(self.filename,tempfile)
        if zipfile.is_zipfile(tempfile):
            zip = zipfile.ZipFile(tempfile,"a")
        else:
            zip = zipfile.ZipFile(tempfile,"w")

        files = self.tempzip.namelist()
        for file in files:
            zip.writestr(str(file),self.tempzip.read(file))
        self.tempzip.close()

        newZip = zipfile.ZipFile(self.filename, "w")
        ET.tostring(self.root, "utf-8")
        newZip.writestr(str(expFilename), ET.tostring(self.root,"UTF-8"))
        images = self.root.findall('ObservationTimePoint/Observation/ObservationImage')
        for img in images:
            if img.text:
                imgName = img.text
                tbName = "tb_" + imgName
                newZip.writestr(str(imgName),zip.read(imgName))
                newZip.writestr(str(tbName),zip.read(tbName))
        zip.close()
        newZip.close()
        os.remove(tempfile)
        self.StartTemp()

def OpenFile(filename, defFile, new=None, userData = None, controller = None):

    backend = XMLBackend(filename, defFile, userData, new)

    # determine program version that created file
    version = backend.GetVersion()
    # pass new XMLFileHandler to the appropriate tray data class
    if backend.rootElement.tag == "Screen" and version == "1.0":
        return tray_data.TrayData(backend, new, userData, controller)
    elif backend.rootElement.tag == "Prefs":
    	# return the same, but pass version string with it.
        return backend
    else:
        return JTrayData(backend, False, userData, controller)


if __name__ == "__main__":
    #defFile = "../../files/Dtd/definition.xml"
    #data = OpenFile("../../files/screens/test.exp",defFile)
    #xml.dom.ext.PrettyPrint(data.doc)
    #data.printDoc()
    xmlFileHandler = XMLFileHandler("U:/Personal/Programming/pyTray/src/test/Experiment.xml", False)
    #xmlFileHandler.GetReport()
    xmlFileHandler.Save("test/test_out.exp")
