#!/usr/bin/env python2.3

"""
Error window that pops up and displays unhandled errors
"""


from wx.lib.dialogs import *
import wx
import sys, traceback

class ErrorDialog(wx.Dialog):
    def __init__(self, parent, msg, caption,
                    pos=wx.DefaultPosition, size=(500,300),
                    style=wx.DEFAULT_DIALOG_STYLE):
            wx.Dialog.__init__(self, parent, -1, caption, pos, size, style)
            x, y = pos
            if x == -1 and y == -1:
                self.CenterOnScreen(wx.BOTH)
    
            self.text = wx.TextCtrl(self, -1, msg, 
                               style=wx.TE_MULTILINE | wx.TE_READONLY)
            okID = wx.NewId()
            ok = wx.Button(self, okID, "OK")
            self.Bind(wx.EVT_BUTTON, self.OnButton, ok)
            self.Bind(wx.EVT_CLOSE, self.OnButton)
            ok.SetDefault()
            lc = layoutf.Layoutf('t=t5#1;b=t5#2;l=l5#1;r=r5#1', (self,ok)) 
            self.text.SetConstraints(lc)
    
            lc = layoutf.Layoutf('b=b5#1;x%w50#1;w!80;h*', (self,))
            ok.SetConstraints(lc)
            self.SetAutoLayout(1)
            self.Layout()

    def OnButton(self, event):
        self.Destroy()

    def write(self, msg):
        self.text.AppendText(msg)

class ErrorHandler:
    def __init__(self):
        self.dialog = None
    def write(self, msg):
        try:
            if not self.dialog:
                self.dialog = ErrorDialog(None, "Ooops, this looks like bug! Please send the error message to schalch@mol.biol.ethz.ch\n\n", "ErrorWindow")
                self.dialog.Show()
            if not self.dialog.IsShown():
                self.dialog = ErrorDialog(None, "Error:", "ErrorWindow")
                self.dialog.Show()
            self.dialog.write(msg)
        except:
            sys.stderr = sys.__stderr__
            print traceback.print_exc(file=sys.stdout)
            raise


class GuiApp(wx.App):
    def OnInit(self):
        return True

if __name__ == "__main__":
    app = GuiApp(0)
    app.MainLoop()
    hdl = ErrorHandler()
    hdl.write("Test")