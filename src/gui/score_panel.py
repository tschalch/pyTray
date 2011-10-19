#!/usr/bin/env python

import wx
import scoring_table

class ScorePanel(wx.Panel):
    def __init__(self, parent, data, controller):
        wx.Panel.__init__(self, parent, -1)
        self.data = data
        self.controller = controller
        self.splitter = wx.SplitterWindow(self, -1)
        comp_widths = [0.2, 0.55, 0.2]
        self.grid_panel = wx.Panel(self.splitter, -1)
        self.lowerPanel = wx.Panel(self.splitter, -1)

        # Buttons
        self.defaultButton = wx.Button(self.lowerPanel, -1, \
                                      "Set as default scoring system")
        self.Bind(wx.EVT_BUTTON, self.OnDefaultButton, self.defaultButton)
        self.replaceButton = wx.Button(self.lowerPanel, -1, \
                                      "Replace with default scoring system")
        self.Bind(wx.EVT_BUTTON, self.OnReplaceButton, self.replaceButton)

        # Grid
        self.score_grid = scoring_table.ScoreGrid(self.grid_panel,\
                                           self.data,\
                                           scoring_table.ScoreDataTable(data),\
                                           comp_widths,\
                                           style = wx.VSCROLL)
        self.data.AddEventListener("score",self.score_grid)
        self.splitter.SplitHorizontally(self.grid_panel, self.lowerPanel, 350)

        self.__do_layout()
        
    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        comp_sizer = wx.BoxSizer(wx.VERTICAL)
        comp_sizer.Add(self.score_grid, 1.0, wx.EXPAND, 0)
        self.grid_panel.SetSizer(comp_sizer)

        lower_sizer = wx.BoxSizer(wx.VERTICAL)
        lower_sizer.Add(self.defaultButton,0,wx.ALL,5)
        lower_sizer.Add(self.replaceButton,0,wx.ALL,5)
        self.lowerPanel.SetSizer(lower_sizer)
        
    def OnDefaultButton(self, event):
        self.controller.userData.SetScoringSystem(self.data.GetScores())
        pass

    def OnReplaceButton(self, event):
        if len(self.data.GetObservationDates()):
            d = wx.MessageBox("Are you sure you want to change your scoring system?\n",\
                             "Confirm", wx.YES_NO, self)
            if d == wx.YES:
                self.data.ImportScores(self.controller.userData)
                self.data.UpdateEventListeners(["score"],self)
        else:
            self.data.ImportScores(self.controller.userData)
            self.data.UpdateEventListeners(["score", "tray"],self)
                    
