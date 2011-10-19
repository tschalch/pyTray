#!/usr/bin/env python

import logging
logging.basicConfig()
log = logging.getLogger("gui")

import wx
import os, os.path, sys
#adding lib directory to module search path
libpath = os.path.abspath(os.path.dirname(sys.argv[0])) + "/lib"
sys.path.append(os.path.abspath(libpath))

# make PIL work with py2exe
#from PIL import Image, ImageFont, ImageDraw, JpegImagePlugin, BmpImagePlugin
#Image.preinit()    # import drivers for every image format you use
#Image._initialized=2

# pytray modules
from gui.error_window import ErrorHandler
from controller import Controller


class GuiApp(wx.App):
    def OnInit(self):
        return True

if __name__ == "__main__":

    wrap = False
    if wrap:
        import wx.py.PyWrap
        wx.py.PyWrap.main("pytray")
    app = GuiApp(False)
    try:
        arg1 = sys.argv[1]
    except IndexError:
        arg1 = None
    
    if not arg1 or (arg1 and os.path.isfile(arg1)):
        ctrlr = Controller(arg1)
        ctrlr.Start()
  
    if arg1:
        # call testing routine
        import test.unittest
        if test.unittest.testmodules.has_key(arg1) or arg1 == "all":
            test.unittest.Testing(arg1)
        
    #sys.stderr = ErrorHandler()
    profiling = False
    if profiling:
        import profile
        profile.run('app.MainLoop()', 'gui_profile')
    else:
        app.MainLoop()

