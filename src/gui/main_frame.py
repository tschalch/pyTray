#!/usr/bin/env python

import logging
logging.basicConfig()
log = logging.getLogger("gui")

import wx
import os, sys, pdb
from util.trayErrors import NoUndoError
from xtal_panel import XtalPanel
from screen_panel import ScreenPanel
from score_panel import ScorePanel
from stock_panel import StockPanel
#from dataStructures.reporting import Report

wildcard = "Experiment Files (*.exp)|*.exp|"     \
           "Screen Files (*.screen)|*.screen|" \
           "All files (*.*)|*.*"

txtwildcard = "cvs file (*.txt)|*.txt|"\
             "All files (*.*)|*.*"

pdf_wildcard = "PDF Files (*.pdf)|*.pdf|"    \
           "All files (*.*)|*.*"


class MainFrame(wx.Frame):
    """
    Main frame of the GUI holding the crystallization experiment.
    """
    
    def __init__(self, data, controller, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self ,*args, **kwds)

        self.controller = controller
        self.data = data
        self.data.AddEventListener("frame",self)
        
        # set program icon
        ib=wx.IconBundle()
        ib.AddIconFromFile(self.controller.path + "/files/images/icon.ico",wx.BITMAP_TYPE_ANY)
        self.SetIcons(ib)        
        # Menu Bar
        MenuBar = wx.MenuBar()
        file_menu = wx.Menu()
        menuItem = file_menu.Append(-1, "New","New file")
        self.Bind(wx.EVT_MENU, self.OnNew, menuItem)
        menuItem = file_menu.Append(-1, "Open","Open file")
        self.Bind(wx.EVT_MENU, self.OnOpen, menuItem)
        menuItem = file_menu.Append(-1, "Save","Save file")
        self.Bind(wx.EVT_MENU, self.OnSave, menuItem)
        menuItem = file_menu.Append(-1, "Save as","Save as different file")
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menuItem)
        menuItem = file_menu.Append(-1, "PDF Report","Generate PDF Reports")
        self.Bind(wx.EVT_MENU, self.OnReport, menuItem)
        menuItem = file_menu.Append(-1, "E&xit","Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnQuit, menuItem)
        MenuBar.Append(file_menu, "&File")

        edit_menu = wx.Menu()
        menuItem = edit_menu.Append(-1, "Undo", "Undo")
        self.Bind(wx.EVT_MENU, self.OnUndo, menuItem)
        menuItem = edit_menu.Append(-1, "Delete", "Delete Screen Solution")
        self.Bind(wx.EVT_MENU, self.OnDelete, menuItem)
        menuItem = edit_menu.Append(-1, "Change Screen Name", "Change Screen Name")
        self.Bind(wx.EVT_MENU, self.OnNameChange, menuItem)
        MenuBar.Append(edit_menu, "&Edit")

        op_menu = wx.Menu()
        menuItem = op_menu.Append(-1, "Initialize Reservoirs",\
                         "Initialize Reservoirs from Screen Solutions")
        self.Bind(wx.EVT_MENU, self.OnInitReservoirs, menuItem)
        menuItem = op_menu.Append(-1, "Remove unused reagents",\
                         "Remove unused stock reagents")
        self.Bind(wx.EVT_MENU, self.OnRemoveUnusedStocks, menuItem)
        menuItem = op_menu.Append(-1, "Import Stock Solutions",\
                         "Import Stock Solutions")
        self.Bind(wx.EVT_MENU, self.OnImportStockSolutions, menuItem)
        menuItem = op_menu.Append(-1, "Import Screen Solutions",\
                         "Import Screen Solutions")
        self.Bind(wx.EVT_MENU, self.OnImportScreenSolutions, menuItem)
        menuItem = op_menu.Append(-1, "Import Formulation from cvs file",\
                         "Import Formulation from cvs file")
        self.Bind(wx.EVT_MENU, self.OnImportFromCvs, menuItem)
        menuItem = op_menu.Append(-1, "Import stock reagents from cvs file",\
                         "Import stock reagents from cvs file")
        self.Bind(wx.EVT_MENU, self.OnImportStocksFromCvs, menuItem)
        menuItem = op_menu.Append(-1, "Import simplex screen from cvs file",\
                         "Import simplex screen from cvs file")
        self.Bind(wx.EVT_MENU, self.OnImportScreenFromSimplexCvs, menuItem)
        menuItem = op_menu.Append(-1, "Export Data",\
                         "Export Data for Analysis")
        self.Bind(wx.EVT_MENU, self.OnGetAnalysisData, menuItem)
        menuItem = op_menu.Append(-1, "Export Simplex Data",\
                         "Export Data for Simplex Analysis")
        self.Bind(wx.EVT_MENU, self.OnGetSimplexData, menuItem)
        MenuBar.Append(op_menu, "&Operations")

        scr_menu = wx.Menu()
        menuItem = scr_menu.Append(-1, "Random Generator",\
                         "Distribute reagents randomly based on frequency")
        self.Bind(wx.EVT_MENU, self.OnRandomGeneration, menuItem)
        MenuBar.Append(scr_menu, "&Screen")

        self.SetMenuBar(MenuBar)
        # end Menu Bar
        
        # Event handling
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        

        if self.data:
            # organize panels in notebook
            self.notebook = wx.Notebook(self, -1, style=0)
            # panel holding crystallization experiment and observations
            self.xtal_panel = XtalPanel(self.notebook, self.data)
            # panel for screen information
            self.screen_panel = ScreenPanel(self.notebook, self.data)
            # panel for stock solutions
            self.stock_panel = StockPanel(self.notebook, self.data)
            # panel for scoring system
            self.score_panel = ScorePanel(self.notebook, self.data, self.controller)
            self.__do_layout()
            self.__set_properties()
        else:
            self.OpenTray()

    def __set_properties(self):
        self.SetTitle("pyTray - %s - %s" % (self.data.GetScreenName(), self.data.GetFilename()))
  
        #get screen resolution
        (x,y) = wx.DisplaySize()
  
        #resize frame
        self.SetSize((int(x*0.6),int(y*0.8)))
          
        #center frame on screen
        self.Centre(wx.BOTH)

        self.SetSize((560, 830))
        
    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.notebook.AddPage(self.xtal_panel, "Crystal Tray")
        self.notebook.AddPage(self.screen_panel, "Screen Solutions")
        self.notebook.AddPage(self.stock_panel, "Stock Solutions")
        self.notebook.AddPage(self.score_panel, "Scoring System")
        sizer_1.Add(self.notebook, 1, wx.EXPAND, 0)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Fit()
        self.Layout()

    def OnDataChange(self):
        self.SetTitle("pyTray - %s - %s" % (self.data.GetScreenName(), self.data.GetFilename()))

    def OnDelete(self,event):
        self.data.DeleteScreenSolutions()        
        
    def OnNameChange(self, event):
        name = self.data.GetScreenName()
        d = wx.GetTextFromUser("Please change screen name", "Screen name:", name, self)
        if d:
            self.data.SetScreenName(d)
            self.data.UpdateEventListeners(["frame"],self)

    def OnQuit(self,event):
        self.controller.userData.SetValue("LastDir", os.getcwd())
        if self.data:
            if self.data.HasChanged():
                answer = wx.MessageBox("There are unsaved changes. Are you sure you want to quit?", \
                "Confirmation", wx.YES_NO)
                if answer == wx.YES:
                    self.Destroy()
            else:
                self.Destroy()
        else:
            self.Destroy()

    def OnOpen(self,event):
        self.controller.OpenTray(self)
        
    def OnInitReservoirs(self, event):
        d = wx.MessageBox("Reservoir settings will be overwritten!\n Do you want to proceed?",\
                         "Confirm", wx.YES_NO, self)
        if d == wx.YES:
            self.data.InitReservoirsFromScreen()
            self.xtal_panel.tray.RefreshWells()
            self.screen_panel.tray.RefreshWells()
            self.data.UpdateEventListeners(["front"],self)
        
    def OnImportStockSolutions(self,event):
        d = wx.MessageBox("Screen solutions and reservoir information will be deleted!",\
                         "Confirm", wx.YES_NO, self)
        if d == wx.YES:
            source = self.controller.GetTrayData(self)
            self.data.ImportStockSolutions(source)
            self.data.UpdateEventListeners(["reagents","screen"],self)

    def OnImportScreenSolutions(self,event):
        d = wx.MessageBox("Stock soutions, screen solutions and reservoir information will be deleted!",\
                         "Confirm", wx.YES_NO, self)
        if d == wx.YES:
            source = self.controller.GetTrayData(self)
            self.data.ImportStockSolutions(source)
            self.data.ImportScreenSolutions(source)
            self.data.InitReservoirsFromScreen()
            self.xtal_panel.tray.RefreshWells()
            self.screen_panel.tray.RefreshWells()
            self.data.UpdateEventListeners(["front","reagents","screen"],self)

    def OnImportFromCvs(self,event):
        self.ImportFromCvs(event,"formulations")

    def OnImportStocksFromCvs(self,event):
        self.ImportFromCvs(event,"stocks")

    def OnImportScreenFromSimplexCvs(self,event):
        self.ImportFromCvs(event,"screen")

    def ImportFromCvs(self,event,type):
        msg = "Screen solutions and reservoir information will be deleted!\n\n"\
                           "Importing from cvs (comma separated) text file.\n"\
                           "Lines starting with '#' will be ignored.\n"\
                           "Lines starting with '>' will be treated as headings.\n"
        if type == "formulations":
            msg += "The field 'SolutionNr' references the number of the solution in the original screen.\n"\
                   "The 'Position' field specifies the well position in the new screen."
        d = wx.MessageBox(msg, "Confirm", wx.YES_NO, self)
        if d == wx.YES:
            dir = self.controller.userData.GetValue("LastDir")
            dlg = wx.FileDialog(
                self, message="Choose cvs file", defaultDir=dir, 
                defaultFile="", style=wx.OPEN | wx.CHANGE_DIR
                )
            # Show the dialog and retrieve the user response. If it is the OK response, 
            # process the data.
            if dlg.ShowModal() == wx.ID_OK:
                self.controller.userData.SetValue("LastDir", os.getcwd())
                # This returns a Python list of files that were selected.
                path = dlg.GetPath()
                if os.access(path, os.F_OK):
                            from util.converter import Converter
                            converter = Converter(path, self.data)
                            if type == "formulations":
                                converter.convert()
                            elif type == "stocks":
                                converter.convertStocks()
                            elif type == "screen":
                                converter.convertSimplexScreen()
                            self.data.UpdateEventListeners(["reagents","screen"],self)
                            self.data.InitReservoirsFromScreen()
                            self.xtal_panel.tray.RefreshWells()
                            self.screen_panel.tray.RefreshWells()
                            self.data.UpdateEventListeners(["front"],self)

    def OnGetAnalysisData(self, event):
        self.SaveAs(self.data.SaveAnalysisData,txtwildcard)
        wx.MessageBox("Data has been exported", "Message", wx.OK)

    def OnGetSimplexData(self, event):
        self.SaveAs(self.data.SaveSimplexData,txtwildcard)
        wx.MessageBox("Data has been exported", "Message", wx.OK)
    
    def OnNew(self, event):
        self.controller.NewTray(self)

    def OnRandomGeneration(self, event):
        from util.screen_generator import ScreenGenerator
        generator = ScreenGenerator(self.data)
        generator.CreateRandomScreen()
    
    def OnRemoveUnusedStocks(self,event):
        self.data.RemoveUnusedReagents()
        self.data.UpdateEventListeners(["reagents"],self)
    
    def OnSave(self,event):
        if self.data.GetFilename() != "Untitled":
            self.data.Save() 
        else:
            self.OnSaveAs(event)
        pass

    def OnSaveAs(self,event):
        self.SaveAs(self.data.Save, wildcard)

    def OnReport(self,event):
        from dataStructures.reporting import Report
        dir = self.controller.userData.GetValue("LastDir")
        choiceList = ["Result Sheet", "Scoring Sheet", "Scoring Graphics", "Screen Solutions", "Screen Pipetting Scheme", "Stock Solutions"]
        partList = ["scoreList", "emptyScoringSheet","scoreGraphics","screenSols", "screenVolumes","stockSols"]
        parts = {}
        choiceBox = wx.MultiChoiceDialog(self, "Choose for printing:", "Choicebox",choiceList)
        if choiceBox.ShowModal() == wx.ID_OK:
            choices = choiceBox.GetSelections()
            for i in range(len(partList)):
                if choices.count(i) > 0:
                    if partList[i] == "screenVolumes":
                        d = wx.GetTextFromUser ("Please enter the volume with unit.\nFor example: \"10 ml\"", "Input Volume",\
                                            "10 ml", self,)
                        if d:
                            screenVolume = d.split(' ')
                            try:
                                screenVolume[0] = float(screenVolume[0])
                                if len(screenVolume) == 2:
                                    parts[partList[i]] = screenVolume
                                else:
                                    parts[partList[i]] = 0
                            except:
                                parts[partList[i]] = 0
                                print "Screen Volume Input Invalid"
                        else:
                            parts[partList[i]] = 0
                    else:
                        parts[partList[i]] = 1
                else:
                    parts[partList[i]] = 0
            dlg = wx.FileDialog(
                self, message="Save Report to", defaultDir=dir, 
                defaultFile=self.data.GetFilename().split('.')[0], wildcard=pdf_wildcard, style=wx.SAVE | wx.CHANGE_DIR
                )
            # Show the dialog and retrieve the user response. If it is the OK response, 
            # process the data.
            if dlg.ShowModal() == wx.ID_OK:
                self.controller.userData.SetValue("LastDir", os.getcwd())
                # This returns a Python list of files that were selected.
                path = dlg.GetPath()
                if os.access(path, os.F_OK):
                    d = wx.MessageBox("Overwrite existing file?", "Confirm", wx.YES_NO, self)
                    if d == wx.YES:
                        report = Report(self.data,parts, self.xtal_panel.tray, path, self.controller.userData.GetTempDir())
                        gen = report.compile()
                else:
                    report = Report(self.data,parts, self.xtal_panel.tray, path. self.controller.userData.GetTempDir())
                    gen = report.compile()
            dlg.Destroy()
            if gen[0]:
                #wx.MessageBox(gen[1], "Message", wx.OK)
                #os.startfile(path)
		os.system('open %s' % path)
            else:
                wx.MessageBox(gen[1], "Message", wx.OK)

    def OnUndo(self, event):
        try:
            self.xtal_panel.tray.ClearWells()
            self.screen_panel.tray.ClearWells()
            self.data.Undo()
            self.screen_panel.tray.RefreshWells()
            self.xtal_panel.tray.RefreshWells()
        except NoUndoError, e:
            d = wx.MessageBox("No more undo actions, sorry.", "Warning", wx.OK, self)

    def SaveAs(self, saveFunction, wildcard):
        dir = self.controller.userData.GetValue("LastDir")
        dlg = wx.FileDialog(
            self, message="Save as", defaultDir=dir, 
            defaultFile="", wildcard=wildcard, style=wx.SAVE | wx.CHANGE_DIR
            )
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            self.controller.userData.SetValue("LastDir", os.getcwd())
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()
            if os.access(path, os.F_OK):
                d = wx.MessageBox("Overwrite existing file?", "Confirm", wx.YES_NO, self)
                if d == wx.YES:
                    saveFunction(path)
            else:
                saveFunction(path)
        dlg.Destroy()
        self.data.UpdateEventListeners(["frame"],self)
        
            
"""
Testing code
****************************************
"""

import controller

class GuiApp(wx.App):

    def OnInit(self):
        self.controller = controller.Controller(["U:/Personal/Programming/pyTray/src/","//xtend/biopshare/Thomas/Screens/pyTray_Files/test.exp"], self)
        self.controller.Start()
        return True

if __name__ == "__main__":
#if True:
    app = GuiApp(0)
    profiling = False
    if profiling:
        import profile
        profile.run('app.MainLoop()', 'gui_profile')
    else:
        app.MainLoop()
