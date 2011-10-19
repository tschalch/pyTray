#-----------------------------------------------------------------------------
# Name:        controller.py
# Purpose:     Top level module that manages file opening and generation
#              of new pyTray frames
#
# Author:      Thomas Schalch
#
# Created:     2006/03/28
# RCS-ID:      $Id: controller.py,v 1.6 2007/08/15 17:54:08 schalch Exp $
# Copyright:   (c) 2004
# Licence:     <your licence>
#-----------------------------------------------------------------------------

import wx
import wx.lib.dialogs
import os, os.path, sys 
from gui.main_frame import MainFrame 
from gui.welcome import WelcomeFrame 
from dataStructures.user_data import UserData
from dataStructures.elmtree_backend import OpenFile
import dataStructures.tray_data

wildcard = "Experiment Files (*.exp)|*.exp|"     \
           "Screen Files (*.screen)|*.screen|" \
           "All files (*.*)|*.*"

class Controller:
    def __init__(self, file):
        self.file = file
        self.path = os.path.abspath(os.path.dirname(sys.argv[0]))
        sys.path.append(os.path.dirname(self.path))
        # frames list
        self.frames = []
        # definition File
        self.defFile = os.path.abspath(self.path + "/files/Dtd/definition.xml")
        # User Preferences
        self.userTemplateFile = os.path.abspath(self.path + "/files/user.pyTray")
        self.userData = UserData(self)
        if file:
            try:
                self.file = file
                self.data = OpenFile(self.file, self.defFile, False, self.userData, self)
            except IndexError:
                self.file = None
            except IOError:
                self.file = None

    def Start(self):
        if self.file:
            frame = MainFrame(self.data, self , None, -1, "pyTray - " + self.file)
            self.frames.append(frame)
            frame.Show(True)
            #frame.Center()
            self.userData.SetValue("LastDir", os.path.dirname(self.file))
            #dialog for error messages
            return frame
        else:
            self.welcomScreen = WelcomeFrame(self)
            self.welcomScreen.Show(True)
            file = None

    def OpenTray(self, caller):
        dir = self.userData.GetValue("LastDir")
        dlg = wx.FileDialog(
            caller, message="Choose a file", defaultDir=dir, 
            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR | wx.MULTIPLE
            )
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            self.userData.SetValue("LastDir", os.getcwd())
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()
            for i in range(len(paths)):
                file = paths[i]
                data = OpenFile(file, self.defFile, False, self.userData)
                frame = MainFrame(data, self , None, -1, "pyTray - " + file)
                self.frames.append(frame)
                frame.Show(True)
                #frame.CenterOnScreen()
                #position = frame.GetPosition()
                #frame.MoveXY(position[0] + i * 10, position[1] + i * 5)
            return True
        dlg.Destroy()
        
    def GetTrayData(self, caller, file = None):
        if not file:
            dir = self.userData.GetValue("LastDir")
            dlg = wx.FileDialog(caller, message="Choose a file", defaultDir=dir, 
                defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
                )
            # Show the dialog and retrieve the user response. If it is the OK response, 
            # process the data.
            if dlg.ShowModal() == wx.ID_OK:
                self.userData.SetValue("LastDir", os.getcwd())
                # This returns a Python list of files that were selected.
                path = dlg.GetPath()
                data = OpenFile(path, self.defFile, userData = self.userData, controller = self)
                return data
            dlg.Destroy()
        else:
            return OpenFile(file, self.defFile, userData = self.userData)
                
    def NewTray(self, caller, testData=False):
        if testData:
            source, screen = testData
            fromScratch = 1
            if source:
                fromScratch = 0
        else:
            dir = self.userData.GetValue("LastDir")
            try:
                os.chdir(dir)
            except:
                pass
            newDlg = NewDialog(caller, -1, "New Screen Dialog", size=(200,350),
                            style = wx.DEFAULT_DIALOG_STYLE)
            newDlg.CenterOnScreen()
            val = newDlg.ShowModal()
            while(val == wx.ID_OK and not newDlg.GetScreen()):
                val = newDlg.ShowModal()
            if val == wx.ID_OK:
                screen = newDlg.GetScreen()
                fromScratch = 0
                try:
                    source = newDlg.data
                except AttributeError:
                    fromScratch = 1
            else:
                newDlg.Destroy()
                return False
            
        data = OpenFile(None, self.defFile, new = screen, userData = self.userData)
        if not fromScratch:
            data.ImportReagents(source)
            data.ImportScreenSolutions(source)
            data.ImportReservoirs(source)
            data.ImportScores(source)
        else:
            data.ImportScores(self.userData)

        if testData:
            return data
        frame = MainFrame(data, self, None, -1, "pyTray")
        frame.Show(True)
        frame.CenterOnScreen()
        newDlg.Destroy()
        return True
            
        dlg = wx.FileDialog(
            caller, message="Choose a file", 
            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            self.userData.SetValue("LastDir", os.getcwd())
            # This returns a Python list of files that were selected.
            file = dlg.GetFilename()
            if os.access(file, os.F_OK):
                d = wx.MessageBox("Overwrite existing file?", "Confirm", \
                                    wx.YES_NO|wx.ICON_EXCLAMATION, caller)
            else:
                d = wx.YES
                
            if d == wx.YES:
                newScreen = {"ScreenName":"testScreen", "NoRows":"4", "NoCols":"6", "NoDrops":"1", \
                    "WellVolume":"10000", "VolumeUnit":"ul"}
                data = OpenFile(file, self.defFile, newScreen, self.userData)
                frame = MainFrame(data, self, None, -1, "pyTray")
                frame.Show(True)
                return True
        dlg.Destroy()
        
        
class NewDialog(wx.Dialog):

    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)
        self.controller = parent.controller
        fieldHeight = 20
        sizer_0 = wx.FlexGridSizer(3,1,0,0)
        # Template fields
        box = wx.BoxSizer(wx.HORIZONTAL)
        templateLabel = wx.StaticText(self, -1, "Import screen from: ")
        box.Add(templateLabel, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.templateField = wx.TextCtrl(self, -1, size = (50,fieldHeight))
        box.Add(self.templateField, 3, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        TEMPLATE_ID = wx.NewId()
        templateBtn = wx.Button(self, TEMPLATE_ID, " Choose File ")
        self.Bind(wx.EVT_BUTTON, self.OnTemplate, templateBtn)
        box.Add(templateBtn, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizer_0.Add(box, 0, 0,0)
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer_0.Add(line, 0, wx.EXPAND,0)
        # Screen name field
        box = wx.BoxSizer(wx.HORIZONTAL)
        nameLabel = wx.StaticText(self, -1, "Screen Name:")
        box.Add(nameLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.nameField = wx.TextCtrl(self, -1, size = (200,fieldHeight), name="Screen Name")
        box.Add(self.nameField, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizer_0.Add(box, 0, wx.EXPAND,0)
        # Rows/Cols fields
        box = wx.BoxSizer(wx.HORIZONTAL)
        rowsLabel = wx.StaticText(self, -1, "Nr. of Rows:")
        box.Add(rowsLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.rowsField = wx.TextCtrl(self, -1, size = (50,fieldHeight), style = wx.TE_CENTRE)
        box.Add(self.rowsField, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        colsLabel = wx.StaticText(self, -1, "Columns:")
        box.Add(colsLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.colsField = wx.TextCtrl(self, -1, size = (50,fieldHeight), style = wx.TE_CENTRE)
        box.Add(self.colsField, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        dropsLabel = wx.StaticText(self, -1, "Drops/Well:")
        box.Add(dropsLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.dropsField = wx.TextCtrl(self, -1, size = (50,fieldHeight), style = wx.TE_CENTRE)
        box.Add(self.dropsField, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizer_0.Add(box, 0, 0,0)
        # OK/Cancel Buttons
        box = wx.BoxSizer(wx.HORIZONTAL)
        okBtn = wx.Button(self, wx.ID_OK, " OK ")
        okBtn.SetDefault()
        cancelBtn = wx.Button(self, wx.ID_CANCEL, " Cancel ")
        box.Add(okBtn, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box.Add(cancelBtn, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizer_0.Add(box, 0, wx.ALIGN_CENTER_HORIZONTAL,0)
        self.SetSizer(sizer_0)
        self.SetAutoLayout(True)
        sizer_0.Fit(self)

    def GetScreen(self):
        try:
            name = str(self.nameField.GetValue())
            noRows = int(self.rowsField.GetValue())
            noCols = int(self.colsField.GetValue())
            noDrops = int(self.dropsField.GetValue())
        except:
            return False
        if not name:
            return False
        newScreen = {"ScreenName": name, "NoRows": noRows, \
                    "NoCols":noCols, "NoDrops":noDrops}
        return newScreen

    def OnTemplate(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file", 
            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPaths()
            file = dlg.GetFilename()
            self.templateField.SetValue(path[0])
            self.data = OpenFile(path[0], self.controller.defFile)
            self.rowsField.SetValue(str(self.data.noRows))
            self.rowsField.Disable()
            self.colsField.SetValue(str(self.data.noCols))
            self.colsField.Disable()
            self.dropsField.SetValue(str(self.data.noDrops))
            #self.dropsField.Disable()
            self.nameField.SetValue(str(self.data.GetScreenName()))
        dlg.Destroy()
        pass

# message dialog for errors and log messages
import  wx.lib.dialogs

class LogPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        b = wx.Button(self, -1, "Errors and log messages", (50,50))
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)


    def OnButton(self, evt):
        f = open("Main.py", "r")
        msg = f.read()
        f.close()

        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "message test")
        dlg.ShowModal()
