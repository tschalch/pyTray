#!/usr/bin/env python

import logging
logging.basicConfig()
log = logging.getLogger("gui")

import wx
from PIL import Image
import os, sys
from util.trayErrors import NoUndoError
from observation_panel import ImagePanel

wildcard = "Experiment Files (*.exp)|*.exp|"     \
           "Screen Files (*.screen)|*.screen|" \
           "All files (*.*)|*.*"


class WelcomeFrame(wx.Frame):
    def __init__(self , controller):
        wx.Frame.__init__(self, None)
        images = ['title1.jpg','title2.jpg']
        self.imagePanels = []
        for i in images:
            imagefile = controller.path + "/files/images/" + i
            titleImage = Image.open(imagefile)
            self.imagePanels.append(ImagePanel(self, titleImage, titleImage.size))
        self.controller = controller
        NEW_BUTTON_ID = wx.NewId()
        self.newButton = wx.Button(self, NEW_BUTTON_ID, "New Tray")
        self.Bind(wx.EVT_BUTTON, self.OnNew, self.newButton)
        OPEN_BUTTON_ID = wx.NewId()
        self.openButton = wx.Button(self, OPEN_BUTTON_ID, "Open Tray")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self. openButton)
        self.SetSize((400,300))
        self.__do_layout()
        self.Centre()
        

    def OnClose(self, evt):
        self.Hide()
        frame = wx.PythonDemo(None, "wx.Python: (A Demonstration)")
        frame.Show()
        evt.Skip()  # Make sure the default handler runs too...

    def __do_layout(self):
        sizer_0 = wx.FlexGridSizer(3,1,0,0)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_0.Add(self.imagePanels[0], 0, 0,0)
        sizer_0.SetFlexibleDirection(wx.BOTH)
        sizer_0.Add(sizer_1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        sizer_0.Add(self.imagePanels[1], 0, 0,0)
        sizer_1.Add(self.newButton, 1, wx.EXPAND , 0)
        sizer_1.Add(self.openButton, 1, wx.EXPAND , 0)
        self.SetSizer(sizer_0)
        sizer_0.Fit(self)
        sizer_1.Layout()
        #self.SetAutoLayout(1)
        self.Layout()
        
    def OnOpen(self, event):
        if self.controller.OpenTray(self):
            self.Destroy()
        
    def OnNew(self, event):
        if self.controller.NewTray(self):
            self.Destroy()
        
        




"""
Testing code
###################################3
"""
#
#from dataStructures.xml_jtray import XMLJTrayData
#from dataStructures.xml_tray import XMLTrayData
#import dataStructures.xml_filehandler
#import dataStructures.user_data

#class GuiApp(wx.App):
#    def OnInit(self):
#        wx.InitAllImageHandlers() # called so a PNG can be saved
#        defFile = os.path.dirname(sys.argv[0]) + "/../../files/Dtd/definition.xml"
#        userTemplateFile = os.path.dirname(sys.argv[0]) + "/../../files/.pyTray"
#        userData = user_data.UserData(userTemplateFile)
#        userData.SetValue("defFile", defFile)
#        try:
#            filename = sys.argv[1]
#            data = xml_filehandler.OpenFile(filename, defFile)
#            userData.SetValue("LastDir", filename)
#            frame = ScreenFrame(data, userData, None)
#        except IndexError:
#            frame = ScreenFrame(None, userData, None)
#        #data = XMLJTrayData("../../files/screens/test.exp")
#        
#        #frame.Show(True)
#        welcomScreen = WelcomeFrame(None)
#        welcomScreen.Show(True)

#        ## initialize a drawing
#        ## It doesn't seem like this should be here, but the Frame does
#        ## not get sized until Show() is called, so it doesn't work if
#        ## it is put in the __init__ method.
#        #frame.NewDrawing(None)

#        self.SetTopWindow(frame)

#        return True

#if __name__ == "__main__":
#    app = GuiApp(0)
#    profiling = False
#    if profiling:
#        import profile
#        profile.run('app.MainLoop()', 'gui_profile')
#    else:
#        app.MainLoop()

