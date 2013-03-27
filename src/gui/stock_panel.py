#!/usr/bin/env python

import wx
import reservoirGrid

class StockPanel(wx.SplitterWindow):
    """Display class for the stock reagent tab"""

    def __init__(self, parent, data):
        wx.SplitterWindow.__init__(self, parent, -1)
        self.data = data
        self.data.AddEventListener("reagents",self)

        self.upperPanel = wx.Panel(self,-1)
        self.lowerPanel = wx.Panel(self,-1)

        stock_widths = [0.18,0.08,0.05,0.12,0.05,0.09,0.1,0.05,0.06,0.07,0.1]
        self.stock_grid = reservoirGrid.trayGrid(self.upperPanel,\
                                                 self.data,\
                                                 reservoirGrid.ReagentDataTable(data),\
                                                 stock_widths,\
                                                 size=wx.Size(400,400))
        self.data.AddEventListener("reagents",self.stock_grid)

        self.__do_layout()
        self.Layout()

    def __do_layout(self):
        self.SplitHorizontally(self.upperPanel, self.lowerPanel)
        
        sizer_table = wx.BoxSizer(wx.VERTICAL)
        sizer_table.Add(self.stock_grid, 1, wx.EXPAND, 0)
        self.upperPanel.SetSizer(sizer_table)
        sizer_table.Fit(self.upperPanel)
        sizer_table.SetSizeHints(self.upperPanel)
        lower_sizer = wx.BoxSizer(wx.VERTICAL)
        self.lowerPanel.SetSizer(lower_sizer)
        
    def OnDataChange(self):
        self.Layout()
        pass

