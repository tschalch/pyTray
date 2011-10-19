#! /usr/bin/env python

# Class for storing user-specific data

import reservoirGrid
import wx
import wx.grid as gridlib


class ScoreDataTable(reservoirGrid.TrayDataTable):

    def __init__(self, data):
        reservoirGrid.TrayDataTable.__init__(self, data)
        self.colLabels = ["ScoreNr","Description","Color"]
        self.fields = ["ScoreNr","ScoreText","ScoreColor"]
        self.cellEditors = [0,0,0]
        self.cellRenderers = [0,0,ColourRenderer()]
        
    def DeleteRows(self, rows):
        reservoirGrid.TrayDataTable.DeleteRows(self, rows)
        self.data.UpdateEventListeners(["front"], None)
         
    def GetValue(self, row, col):
        if row == len(self.components):
            return ''
        component = self.components[row][0]
        value = component.GetProperty(self.fields[col])
        return value

    def AppendRows(self, numRows = 1):
##        id = wx.GetTextFromUser("Please enter a new score number", "New Score")
##        if id:
##            try:
##                id = int(id)
##            except ValueError:
##                wx.MessageBox("Invalid input. Please enter integer number", "Message", wx.OK)
##            idExists = False
##            for component in self.components:
##                if int(id) == component[0].GetProperty("ScoreNr"):
##                    idExists = True
##            if idExists:
##                wx.MessageBox("Score number already exists", "Message", wx.OK)
##            else:
        self.data.AddNewScore(9999)
        self.ResetView()
        self.data.UpdateEventListeners(["front"], None)

    def InitComponents(self):
        scores = self.data.GetScores()
        self.components = []
        self.componentIDs = []
        for key,score in scores.items():
            rID = score.GetProperty("ScoreNr")
            self.componentIDs.append(rID)
            c = [score]
            self.components.append(c)

    def SetValue(self, row, col, value):
        if row == len(self.components):
            self.AppendRows()
        if col == 0:
            try:
                id = int(value)
            except ValueError:
                wx.MessageBox("Invalid input. Please enter integer number", "Message", wx.OK)
            idExists = False
            for component in self.components:
                if int(id) == component[0].GetProperty("ScoreNr"):
                    idExists = True
            if idExists:
                wx.MessageBox("Score number already exists. Pleas try again.", "Message", wx.OK)
        component = self.components[row][0]
        component.SetProperty(self.fields[col], value)
        self.data.UpdateEventListeners(["front"], None)

    def GetCellRenderer(self, col):
        return self.cellRenderers[col]


class ScoreGrid(reservoirGrid.trayGrid):

    def __init__(self, parent, data, table, widths, *args, **kwds):
        reservoirGrid.trayGrid.__init__(self, parent, data, table, widths, *args, **kwds)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnDblClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnDblClick)

    def Init(self):
        reservoirGrid.trayGrid.Init(self)
        for c in range(self.GetNumberCols()):
            cellRenderer = self.GetTable().GetCellRenderer(c)
            if cellRenderer:
                for r in range(self.GetNumberRows()):
                    self.SetCellRenderer(r,c,cellRenderer.Clone())

    def OnDblClick(self, event):
        if event.GetCol() == 2:
            dlg = wx.ColourDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                color = dlg.GetColourData().GetColour()
                hexColor = '%02X%02X%02X' % (color.Red(), color.Green(), color.Blue())
                self.SetCellValue(event.GetRow(), event.GetCol(), hexColor)
                self.data.UpdateEventListeners(["score"],self)
        elif event.GetCol() == 0:
            pass
        else:
            event.Skip()

class ColourRenderer(gridlib.PyGridCellRenderer):
    def __init__(self):
        gridlib.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        hexColour = "#" + grid.GetCellValue(row,col)
        if hexColour == "#":
            hexColour = 'WHITE'
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        dc.SetBrush(wx.Brush(hexColour, wx.SOLID))
        rect.Inflate(-2,-2)
        dc.DrawRectangleRect(rect)
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        x = rect.x  
        y = rect.y  
        dc.SetTextForeground(wx.BLACK)
#        dc.DrawText(hexColour, x, y)
        
    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)
    
    def Clone(self):
        return ColourRenderer()


""" Test code
#####################################################
"""
#
#from dataStructures.xml_jtray import XMLJTrayData
#from dataStructures.xml_filehandler import OpenFile
#import os.path, logging, sys
#import wx

#class TestFrame(wx.Frame):
#   def __init__(self):
#       wx.Frame.__init__(self, NULL, -1, "Double Buffered Test",
#                        wx.DefaultPosition,
#                        size=(500,200),
#                        style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)


#       defFile = os.path.dirname(sys.argv[0]) + "/../../files/Dtd/definition.xml"
#       data = OpenFile("../../files/screens/test_newformat.exp", defFile)
#       widths = [0.2, 0.53, 0.2]
#       self.grid = ScoreGrid(self,\
#                                          data,\
#                                          ScoreDataTable(data),\
#                                          widths,\
#                                          style = wx.VSCROLL)
#       self.grid.SetFocus()
#       sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
#       sizer_1.Add(self.grid, 1, wx.EXPAND, 0)
#       self.SetSizer(sizer_1)

#class TrayApp(wx.App):
#   def OnInit(self):
#       frame = TestFrame()
#       frame.Show(True)
#       self.SetTopWindow(frame)
#       return True

#if __name__ == "__main__":
#   logging.basicConfig()
#   app = TrayApp(0)
#   app.MainLoop()
