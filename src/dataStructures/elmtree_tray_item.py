#!/usr/bin/env python2.4

"""
tray_data provides the data for the tray GUI.
It handles the XML data and provides the neccessary interfaces.

"""

import logging, os
import xml.etree.cElementTree as ET
from util.ordereddict import oDict
from util.trayErrors import PropertyNotFoundError
import tray_item

log = logging.getLogger("xml_tray")
log.setLevel(logging.WARN)


class TrayItem(tray_item.TrayItem):
    """
    Parent Class for all items in a tray.
    """

    def __init__(self, element, definition=None, parent=None):
        tray_item.TrayItem.__init__(self)
        self.parent = parent
        self.element = element
        self.definition = definition

    def Delete(self, parent = None):
        if parent:
            self.parent = TrayItem(parent)
        result = self.parent.element.remove(self.element)
        self.SetChanged(True)
        
    def ApplyType(self, data, defType):
        if defType == "int":
            if data == "":
                return None;
            return int(data)
        if defType == "float":
            if data == "":
                return float(0)
            return float(data)
        if defType == "str":
            return unicode(data)
    
    def GetParent(self):
        return self.parent

    def GetCopy(self):
        return TrayItem(ET.XML(ET.tostring(self.element)), self.definition)

    def GetAttribute(self, name):
        return self.element.attrib[name]

    def GetProperty(self, name):
        subelement = self.element.find(name)
        if ET.iselement(subelement):
            data = subelement.text
        elif self.definition and ET.iselement(self.definition.find(name)):
            self.SetProperty(name,'')
            return ''
        else:
            error_str = "%s not found in %s." % (name, self.element.tag)
            log.debug(error_str)
            raise PropertyNotFoundError(error_str)
        if data:
            data = data.strip()
            if ET.iselement(self.definition):
                try:
                    type = self.definition.find(name).text
                    property = self.ApplyType(data, type)
                except ValueError:
                    property = self.ApplyType("", type)
                except AttributeError:
                    return data
            else:
                 property = data
            return property
        if ET.iselement(self.definition):
            try:
                type = self.definition.find(name).text
                return self.ApplyType("", type)
            except AttributeError:
                return ""
        else:
            return ""

    def GetText(self):
        return self.element.text

    def PrettyPrint(self):
        return ET.tostring(self.element)

    def ReplaceChild(self, replacement, toBeReplaced):
        for i in range(len(self.element)):
            if self.element[i] == toBeReplaced.element:
                self.element[i] = replacement.element

    def RemoveChild(self, child):
        if type(child) == type(self):
            self.element.remove(child.element)
        else:
            subelement = self.element.find(child)
            self.element.remove(subelement)

    def SaveState(self, queue, source=1):
        #return
        if source == 1:
            source = self
        if source:
            queue.append([self.parent, source, self.GetCopy()])
        else:
            queue.append([self.parent, None, self.GetCopy()])
    
    def SetAttribute(self, name, value):
        try:
            oldValue = self.element.attrib[name]
        except KeyError:
            oldValue = None
            
        if value != oldValue or oldValue == None :
            self.SetChanged(True)
            self.element.attrib[name] = value

    def SetProperty(self, name, data):
        type = "string"
        property = self.element.find(name)
        if ET.iselement(self.definition) and ET.iselement(property):
            try:
                type = self.definition.find(name).text
                if not self.ApplyType(data, type) == self.GetProperty(name):
                    self.SetChanged(True)
            except ValueError:
                log.debug(data + " is not " + type + ", skipped")
                return
            except AttributeError:
                log.debug("Index error. Element does not exist.")
            except PropertyNotFoundError:
                log.debug("Index error. Element does not exist.")
        if ET.iselement(property):
            property.text = unicode(data)
        else:
            newElement = ET.SubElement(self.element,name)
            newElement.text = unicode(data)

    def SetText(self, text):
        self.element.text = text
        
    def AddChild(self, newItem):
        self.element.append(newItem.element)
        newItem.parent = self
        self.SetChanged(True)

    def GetElement(self):
        return self.element

    def GetChildren(self, name):
        children = []
        kids = self.element.getiterator(name)
        for kid in kids:
            children.append(TrayItem(kid, None, self))
        return children

if __name__ == "__main__":

    import controller
    logging.basicConfig()
    cont = controller.Controller(["U:/Personal/Programming/pyTray/src/","//xtend/biopshare/Thomas/Screens/pyTray_Files/test.exp"])
    print ET.tostring(cont.data.screenElement)
    data.Save()


