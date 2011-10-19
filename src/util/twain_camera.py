import wx

from simple_base import TwainBase

class TwainCamera(TwainBase):
    def __init__(self, caller):
        self.caller = caller
        self.Initialise()
    
    def DisplayImage(self, ImageFileName):
        self.caller.AddImage(ImageFileName)

