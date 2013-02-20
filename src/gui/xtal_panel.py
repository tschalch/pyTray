#!/usr/bin/env python

import wx
import Image
import os, sys, pdb
#from xml_tray import XMLTrayData
import wx.lib.mixins.listctrl  as  listmix
from tray import Tray
import reservoirGrid, scoring_table
from util.trayErrors import NoUndoError
from observation_panel import *
import wx.lib.foldpanelbar as fpb
from wx.lib.splitter import MultiSplitterWindow

#----------------------------------------------------------------------
# different icons for the collapsed/expanded states.
# Taken from standard Windows XP collapsed/expanded states.
#----------------------------------------------------------------------

def GetCollapsedIconData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x8eIDAT8\x8d\xa5\x93-n\xe4@\x10\x85?g\x03\n6lh)\xc4\xd2\x12\xc3\x81\
\xd6\xa2I\x90\x154\xb9\x81\x8f1G\xc8\x11\x16\x86\xcd\xa0\x99F\xb3A\x91\xa1\
\xc9J&\x96L"5lX\xcc\x0bl\xf7v\xb2\x7fZ\xa5\x98\xebU\xbdz\xf5\\\x9deW\x9f\xf8\
H\\\xbfO|{y\x9dT\x15P\x04\x01\x01UPUD\x84\xdb/7YZ\x9f\xa5\n\xce\x97aRU\x8a\
\xdc`\xacA\x00\x04P\xf0!0\xf6\x81\xa0\xf0p\xff9\xfb\x85\xe0|\x19&T)K\x8b\x18\
\xf9\xa3\xe4\xbe\xf3\x8c^#\xc9\xd5\n\xa8*\xc5?\x9a\x01\x8a\xd2b\r\x1cN\xc3\
\x14\t\xce\x97a\xb2F0Ks\xd58\xaa\xc6\xc5\xa6\xf7\xdfya\xe7\xbdR\x13M2\xf9\
\xf9qKQ\x1fi\xf6-\x00~T\xfac\x1dq#\x82,\xe5q\x05\x91D\xba@\xefj\xba1\xf0\xdc\
zzW\xcff&\xb8,\x89\xa8@Q\xd6\xaaf\xdfRm,\xee\xb1BDxr#\xae\xf5|\xddo\xd6\xe2H\
\x18\x15\x84\xa0q@]\xe54\x8d\xa3\xedf\x05M\xe3\xd8Uy\xc4\x15\x8d\xf5\xd7\x8b\
~\x82\x0fh\x0e"\xb0\xad,\xee\xb8c\xbb\x18\xe7\x8e;6\xa5\x89\x04\xde\xff\x1c\
\x16\xef\xe0p\xfa>\x19\x11\xca\x8d\x8d\xe0\x93\x1b\x01\xd8m\xf3(;x\xa5\xef=\
\xb7w\xf3\x1d$\x7f\xc1\xe0\xbd\xa7\xeb\xa0(,"Kc\x12\xc1+\xfd\xe8\tI\xee\xed)\
\xbf\xbcN\xc1{D\x04k\x05#\x12\xfd\xf2a\xde[\x81\x87\xbb\xdf\x9cr\x1a\x87\xd3\
0)\xba>\x83\xd5\xb97o\xe0\xaf\x04\xff\x13?\x00\xd2\xfb\xa9`z\xac\x80w\x00\
\x00\x00\x00IEND\xaeB`\x82' 

def GetCollapsedIconBitmap():
    return wx.BitmapFromImage(GetCollapsedIconImage())

def GetCollapsedIconImage():
    import cStringIO
    stream = cStringIO.StringIO(GetCollapsedIconData())
    return wx.ImageFromStream(stream)

#----------------------------------------------------------------------
def GetExpandedIconData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x9fIDAT8\x8d\x95\x93\xa1\x8e\xdc0\x14EO\xb2\xc4\xd0\xd2\x12\xb7(mI\
\xa4%V\xd1lQT4[4-\x9a\xfe\xc1\xc2|\xc6\xc2~BY\x83:A3E\xd3\xa0*\xa4\xd2\x90H!\
\x95\x0c\r\r\x1fK\x81g\xb2\x99\x84\xb4\x0fY\xd6\xbb\xc7\xf7>=\'Iz\xc3\xbcv\
\xfbn\xb8\x9c\x15 \xe7\xf3\xc7\x0fw\xc9\xbc7\x99\x03\x0e\xfbn0\x99F+\x85R\
\x80RH\x10\x82\x08\xde\x05\x1ef\x90+\xc0\xe1\xd8\ryn\xd0Z-\\A\xb4\xd2\xf7\
\x9e\xfbwoF\xc8\x088\x1c\xbbae\xb3\xe8y&\x9a\xdf\xf5\xbd\xe7\xfem\x84\xa4\
\x97\xccYf\x16\x8d\xdb\xb2a]\xfeX\x18\xc9s\xc3\xe1\x18\xe7\x94\x12cb\xcc\xb5\
\xfa\xb1l8\xf5\x01\xe7\x84\xc7\xb2Y@\xb2\xcc0\x02\xb4\x9a\x88%\xbe\xdc\xb4\
\x9e\xb6Zs\xaa74\xadg[6\x88<\xb7]\xc6\x14\x1dL\x86\xe6\x83\xa0\x81\xba\xda\
\x10\x02x/\xd4\xd5\x06\r\x840!\x9c\x1fM\x92\xf4\x86\x9f\xbf\xfe\x0c\xd6\x9ae\
\xd6u\x8d \xf4\xf5\x165\x9b\x8f\x04\xe1\xc5\xcb\xdb$\x05\x90\xa97@\x04lQas\
\xcd*7\x14\xdb\x9aY\xcb\xb8\\\xe9E\x10|\xbc\xf2^\xb0E\x85\xc95_\x9f\n\xaa/\
\x05\x10\x81\xce\xc9\xa8\xf6><G\xd8\xed\xbbA)X\xd9\x0c\x01\x9a\xc6Q\x14\xd9h\
[\x04\xda\xd6c\xadFkE\xf0\xc2\xab\xd7\xb7\xc9\x08\x00\xf8\xf6\xbd\x1b\x8cQ\
\xd8|\xb9\x0f\xd3\x9a\x8a\xc7\x08\x00\x9f?\xdd%\xde\x07\xda\x93\xc3{\x19C\
\x8a\x9c\x03\x0b8\x17\xe8\x9d\xbf\x02.>\x13\xc0n\xff{PJ\xc5\xfdP\x11""<\xbc\
\xff\x87\xdf\xf8\xbf\xf5\x17FF\xaf\x8f\x8b\xd3\xe6K\x00\x00\x00\x00IEND\xaeB\
`\x82' 

def GetExpandedIconBitmap():
    return wx.BitmapFromImage(GetExpandedIconImage())

def GetExpandedIconImage():
    import cStringIO
    stream = cStringIO.StringIO(GetExpandedIconData())
    return wx.ImageFromStream(stream)

#----------------------------------------------------------------------
class TabPanel(wx.Panel):
     """
     This will be the first notebook tab
     """
     #----------------------------------------------------------------------
     def __init__(self, parent):
         """"""
 
         wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
 
         sizer = wx.BoxSizer(wx.VERTICAL)
         txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
         txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")
 
         sizer = wx.BoxSizer(wx.VERTICAL)
         sizer.Add(txtOne, 0, wx.ALL, 5)
         sizer.Add(txtTwo, 0, wx.ALL, 5)
 
         self.SetSizer(sizer)

class XtalPanel(wx.SplitterWindow):
    def __init__(self, parent, data):
        wx.SplitterWindow.__init__(self, parent, -1)

        self.data = data
        self.parent = parent
        self.lower_panel = wx.Panel(self, -1,wx.DefaultPosition)
        #self.lower_panel = TestSashWindow (self)
        #self.sash1 = wx.SashLayoutWindow(self, -1,wx.DefaultPosition,
        #                          style=wx.NO_BORDER |wx.SW_3D)
        #self.sash1.SetOrientation(wx.LAYOUT_HORIZONTAL)
        #self.sash1.SetAlignment(wx.LAYOUT_TOP)
        #self.sash1.SetSashVisible(wx.SASH_BOTTOM, True)
##        #self.lower_panel.SetExtraBorderSize(10)
##        self.sash2 = wx.SashLayoutWindow(self.lower_panel, -1,wx.DefaultPosition,
##                                  style=wx.NO_BORDER |wx.SW_3D)
##        self.sash2.SetOrientation(wx.LAYOUT_HORIZONTAL)
##        self.sash2.SetAlignment(wx.LAYOUT_BOTTOM)
##        self.sash2.SetSashVisible(wx.SASH_BOTTOM, True)
        
        self.tray = Tray(self, self.data)

        #self.CreateFoldPanel(0)
        self.LayoutLowerPanel()
        self.SplitHorizontally(self.tray, self.lower_panel,320)
	sizer = wx.BoxSizer(wx.VERTICAL)
	sizer.Add(self.nb, 1, wx.ALL|wx.EXPAND, 5)
	self.lower_panel.SetSizer(sizer)

    def LayoutLowerPanel(self):

        self.nb = wx.Notebook(self.lower_panel)
        
        # observation panel
	#self.obsPanel = TabPanel(self.nb)
        obsPanel = ObservationPanel(self.nb, self.data)
        self.tray.AddKeyListener(obsPanel)
        self.nb.AddPage(obsPanel, "Observations") 
	obsPanel.Update()

        # reservoir grid panel
        res_widths = [0.35, 0.18, 0.1, 0.3]
        self.reservoir_grid = reservoirGrid.trayGrid(self.nb,\
                                           self.data,\
                                           reservoirGrid.ReservoirDataTable(self.data),\
                                           res_widths,\
                                           size = wx.Size(-1,90),\
                                           style = wx.VSCROLL)
        self.data.AddEventListener("front",self.reservoir_grid)
        self.nb.AddPage(self.reservoir_grid, "Reservoir") 

        # Drop grid panel
        drop_widths = [0.25, 0.2, 0.1, 0.1, 0.3]
        self.drop_grid = reservoirGrid.trayGrid(self.nb,\
                                      self.data,\
                                      reservoirGrid.DropDataTable(self.data),\
                                      drop_widths,\
                                      size = wx.Size(-1,90),\
                                      style = wx.VSCROLL)
        self.data.AddEventListener("front",self.drop_grid)
        self.nb.AddPage(self.drop_grid, "Drops") 
        # global parameters
        self.panel_global = GlobalParameters(self.nb, self.data)
        self.nb.AddPage(self.panel_global, "Notes") 



    def CreateFoldPanel(self, fpb_flags):

        # recreate the foldpanelbar

        newstyle = (True and [fpb.FPB_VERTICAL] or [fpb.FPB_HORIZONTAL])[0]
        self._pnl = fpb.FoldPanelBar(self.sash1, -1, wx.DefaultPosition,
                                     wx.Size(-1,-1), newstyle,  fpb_flags)

        Images = wx.ImageList(16,16)
        Images.Add(GetExpandedIconBitmap())
        Images.Add(GetCollapsedIconBitmap())
        
        # observation panel
        self.obs_item = self._pnl.AddFoldPanel("Observations", collapsed=True,
                                      foldIcons=Images)
        self.obsPanel = ObservationPanel(self.obs_item, self.data)
        self.tray.AddKeyListener(self.obsPanel)
        self._pnl.AddFoldPanelWindow(self.obs_item, self.obsPanel,
                                     fpb.FPB_ALIGN_WIDTH, 0, 0) 

        # reservoir grid panel
        #self._pnl2 = fpb.FoldPanelBar(self.sash2, -1, wx.DefaultPosition,
        #                             wx.Size(-1,-1), fpb.FPB_DEFAULT_STYLE|newstyle,  fpb_flags)
        self.res_item = self._pnl.AddFoldPanel("Reservoir", collapsed=True,
                                      foldIcons=Images)
        res_widths = [0.35, 0.18, 0.1, 0.3]
        self.reservoir_grid = reservoirGrid.trayGrid(self.res_item,\
                                           self.data,\
                                           reservoirGrid.ReservoirDataTable(self.data),\
                                           res_widths,\
                                           size = wx.Size(-1,90),\
                                           style = wx.VSCROLL)
        self.data.AddEventListener("front",self.reservoir_grid)
        self._pnl.AddFoldPanelWindow(self.res_item, self.reservoir_grid,
                                     fpb.FPB_ALIGN_WIDTH, 0, 0) 
        # Drop grid panel
        self.drop_item = self._pnl.AddFoldPanel("Drop", collapsed=True,
                                      foldIcons=Images)
        drop_widths = [0.25, 0.2, 0.1, 0.1, 0.3]
        self.drop_grid = reservoirGrid.trayGrid(self.drop_item,\
                                      self.data,\
                                      reservoirGrid.DropDataTable(self.data),\
                                      drop_widths,\
                                      size = wx.Size(-1,90),\
                                      style = wx.VSCROLL)
        self.data.AddEventListener("front",self.drop_grid)
        self._pnl.AddFoldPanelWindow(self.drop_item, self.drop_grid,
                                     fpb.FPB_ALIGN_WIDTH, 0, 0) 
        # global parameters
        self.global_item = self._pnl.AddFoldPanel("Experimental parameters like setup date, temperature, ect.:",
                                                    collapsed=True, foldIcons=Images)
        self.panel_global = GlobalParameters(self.global_item, self.data)
        self._pnl.AddFoldPanelWindow(self.global_item, self.panel_global,
                                     fpb.FPB_ALIGN_WIDTH, 0, 0) 


class ReservoirList(wx.Panel):
    """
    GUI component that lists reservoir components
    data = tray_data derived object
    """

    fields = ["Reagent","Concentration","Remarks"]

    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent, -1)
        self.list = TrayListCtrl(self, ID_LIST_EDIT, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.data = data
        self.data.AddEventListener(self)
        self.title = wx.StaticText(self, -1, "Reservoir composition:")
        sizer_1 = wx.FlexGridSizer(2,1,0,0)
        sizer_1.AddGrowableCol(0)
        sizer_1.Add(self.title, 0, wx.EXPAND, 0)
        sizer_1.Add(self.list, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)      
        for i,f in enumerate(self.fields):
            self.list.InsertColumn(i,f)
        self.Init()
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEdit, self.list)        

    def OnEdit(self, event):
        log.info("Edited")
        
    def Init(self):
        self.list.DeleteAllItems()
        reservoir = self.data.GetActiveReservoir()
        print "reservoir: %s" % reservoir
        if reservoir:
            components = reservoir.GetChildren("Component")
            if components:
                dataFields = components[0].fields
                for i,component in enumerate(components):
                    reagent = self.data.GetReagent(component.GetProperty(dataFields[0]))
                    self.list.InsertStringItem(i, reagent.GetProperty("name"))
                    self.list.SetStringItem(i,1,str(component.GetProperty(dataFields[1]))+" "+reagent.GetProperty("unit"))

    def OnDataChange(self):
        self.Init()

class TrayListCtrl(wx.ListCtrl,
                   listmix.ListCtrlAutoWidthMixin,
                   listmix.TextEditMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.TextEditMixin.__init__(self)


class GlobalParameters(wx.Panel):
    """
    GUI component that displays remarks, setup date that are 
    global to the experiment
    """
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent, -1)
        self.data = data
        #self.data.AddEventListener(self)
        remarkBoxID = wx.NewId()
        self.remark_box = wx.TextCtrl(self, remarkBoxID, "", style=\
                          wx.TE_MULTILINE|wx.TE_RICH,
                          size = (-1, 60))
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.remark_box, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(parent)
    
        self.Bind(wx.EVT_TEXT, self.OnText, self.remark_box)
        self.Init()

    def Init(self):
        self.remarkText = self.data.GetExperimentParams()
        self.remark_box.SetValue(self.remarkText)
        
    def OnText(self, event):
        text = self.remark_box.GetValue()
        self.data.SetExperimentParams(text)

    def OnDataChange(self):
        pass

class DropList(wx.Panel):
    """
    GUI component that lists drop components
    data = tray_data derived object
    """

    fields = ["Sample","Concentration","Buffer","Volume"]

    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent, -1)
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.data = data
        self.data.AddEventListener("front", self)
        self.title = wx.StaticText(self, -1, "Drop composition:")
        drop = self.data.GetDrop((0,0))
        sizer_1 = wx.FlexGridSizer(2,1,0,0)
        sizer_1.AddGrowableCol(0)
        sizer_1.Add(self.title, 0, wx.EXPAND, 0)
        sizer_1.Add(self.list, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)

        for i,f in enumerate(drop.GetChildren("DropComponent")[0].fields):
            self.list.InsertColumn(i,f)

        self.Init()

    def Init(self):
        self.list.DeleteAllItems()
        drops = self.data.GetActiveDrops()
        if len(drops) == 1:
            dropComponents = self.data.GetDrop(drops[0]).GetChildren("DropComponent")
            if dropComponents:
                for dc in dropComponents:
                    self.list.InsertStringItem(0, dc.GetProperty(dc.fields[0]))
                    for i in range(1, len(dc.fields)):
                        self.list.SetStringItem(0,i,str(dc.GetProperty(dc.fields[i])))


    def OnDataChange(self):
        self.Init()


class TestSashWindow(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        winids = []

        # Create some layout windows
        # A window like a toolbar
        topwin = wx.SashLayoutWindow(
            self, -1, wx.DefaultPosition, (200, 30), 
            wx.NO_BORDER|wx.SW_3D
            )

        topwin.SetDefaultSize((1000, 30))
        topwin.SetOrientation(wx.LAYOUT_HORIZONTAL)
        topwin.SetAlignment(wx.LAYOUT_TOP)
        topwin.SetBackgroundColour(wx.Colour(255, 0, 0))
        topwin.SetSashVisible(wx.SASH_BOTTOM, True)

        self.topWindow = topwin
        winids.append(topwin.GetId())

        # A window like a statusbar
        bottomwin = wx.SashLayoutWindow(
                self, -1, wx.DefaultPosition, (200, 30), 
                wx.NO_BORDER|wx.SW_3D
                )

        bottomwin.SetDefaultSize((1000, 30))
        bottomwin.SetOrientation(wx.LAYOUT_HORIZONTAL)
        bottomwin.SetAlignment(wx.LAYOUT_BOTTOM)
        bottomwin.SetBackgroundColour(wx.Colour(0, 0, 255))
        bottomwin.SetSashVisible(wx.SASH_TOP, True)

        self.bottomWindow = bottomwin
        winids.append(bottomwin.GetId())

        # A window to the left of the client window
        leftwin1 =  wx.SashLayoutWindow(
                self, -1, wx.DefaultPosition, (200, 30), 
                wx.NO_BORDER|wx.SW_3D
                )

        leftwin1.SetDefaultSize((120, 1000))
        leftwin1.SetOrientation(wx.LAYOUT_VERTICAL)
        leftwin1.SetAlignment(wx.LAYOUT_LEFT)
        leftwin1.SetBackgroundColour(wx.Colour(0, 255, 0))
        leftwin1.SetSashVisible(wx.SASH_RIGHT, True)
        leftwin1.SetExtraBorderSize(10)
        textWindow = wx.TextCtrl(
                        leftwin1, -1, "", wx.DefaultPosition, wx.DefaultSize, 
                        wx.TE_MULTILINE|wx.SUNKEN_BORDER
                        )

        textWindow.SetValue("A sub window")

        self.leftWindow1 = leftwin1
        winids.append(leftwin1.GetId())


        # Another window to the left of the client window
        leftwin2 = wx.SashLayoutWindow(
                self, -1, wx.DefaultPosition, (200, 30), 
                wx.NO_BORDER|wx.SW_3D
                )

        leftwin2.SetDefaultSize((120, 1000))
        leftwin2.SetOrientation(wx.LAYOUT_VERTICAL)
        leftwin2.SetAlignment(wx.LAYOUT_LEFT)
        leftwin2.SetBackgroundColour(wx.Colour(0, 255, 255))
        leftwin2.SetSashVisible(wx.SASH_RIGHT, True)

        self.leftWindow2 = leftwin2
        winids.append(leftwin2.GetId())

        # will occupy the space not used by the Layout Algorithm
        self.remainingSpace = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

    def OnSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
