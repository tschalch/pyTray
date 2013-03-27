#!/usr/bin/env python

import wx
from tray import Tray
import reservoirGrid

class ScreenPanel(wx.Panel):
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent, -1)
        self.data = data
        self.data.AddEventListener("screen", self)

        self.splitter = wx.SplitterWindow(self, -1)
        isScreen = True
        self.tray = Tray(self.splitter, self.data, isScreen)
        comp_widths = [0.35, 0.2, 0.1, 0.3]
        self.composition_panel = wx.Panel(self.splitter, -1)
#        self.composition_grid = reservoirGrid.testGrid(self.composition_panel,
#                                        self.data,
#                                        reservoirGrid.ScreenSolutionDataTable(data))
        self.composition_grid = reservoirGrid.trayGrid(self.composition_panel,\
                                           self.data,\
                                           reservoirGrid.ScreenSolutionDataTable(data),\
                                           comp_widths,\
                                           style = wx.VSCROLL)
        self.data.AddEventListener("screen",self.composition_grid)
        self.splitter.SplitHorizontally(self.tray, self.composition_panel)
        self.__do_layout()
        
    def __do_layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.splitter, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        comp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        comp_sizer.Add(self.composition_grid, 1.0, wx.EXPAND, 0)
        self.composition_panel.SetSizer(comp_sizer)

    def OnDataChange(self):
        self.Layout()
        pass
