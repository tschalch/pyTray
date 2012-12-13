"""
    drawingOnGridColumnLabel.py
    2003-12-03

    This example shows a wx.Grid with some sample columns, where the column
    headers draw sort indicators when clicked. The example does not actually
    do the sorting of the data, as it is intended to show how to draw on the
    grid's column headers.

    by Paul McNett (p@ulmcnett.com) and whoever wrote the GridCustTable.py demo,
    from which I pulled the CustomDataTable() class.

    I didn't know what to do until Robin pointed out an undocumented method in
    wx.Grid: GetGridColLabelWindow(), which returns a reference to the wx.Window
    that makes up the column header for the grid. From there, I could trap that
    window's Paint event, and draw the column labels myself, including graphical
    sort indicators.
"""

import wx
import wx.grid as gridlib
import sys, logging
import wx.lib.colourdb as cdb
import util.ordereddict as oDict
# debugging with winpdb:
#import rpdb2
#rpdb2.start_embedded_debugger("test")

log = logging.getLogger("reservoirGrid")
log.setLevel(logging.DEBUG)


class TrayDataTable(gridlib.PyGridTableBase):
    """
    From the wx.Python demo
    """

    def __init__(self, data):
        gridlib.PyGridTableBase.__init__(self)
        self.data = data
        self.InitComponents()
        self.noRows = 0
        self.noCols = 0
        self.initComps = False

    def AppendRows(self, numRows = 1):
        self.data.AddNewComponent(self.GetComponentContainingItem)
        self.ResetView()

    def DeleteRows(self, rows):
        rows.reverse()
        for row in rows:
            for comp in self.components[row]:
                comp.SaveState(self.data.undoQueue, None)
                comp.Delete()
        self.ResetView()
        self.data.SaveBackup()

    #--------------------------------------------------
    # required methods for the wx.grid.PyGridTableBase interface

    def GetNumberRows(self):
        self.currentRows = len(self.components) + 1
        return len(self.components) + 1

    def GetNumberCols(self):
        self.currentColumns = len(self.colLabels)
        return len(self.colLabels)

    def IsEmptyCell(self, row, col):
        pass

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.

    def ResetView(self):
        self.InitComponents()
        """Trim/extend the control's rows and update all values""" 
        self.grid.BeginBatch() 
        for current, new, delmsg, addmsg in [ 
                (self.currentRows, self.GetNumberRows(), gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED), 
                (self.currentColumns, self.GetNumberCols(), gridlib.GRIDTABLE_NOTIFY_COLS_DELETED, gridlib.GRIDTABLE_NOTIFY_COLS_APPENDED), 
        ]: 
                if new < current: 
                        msg = gridlib.GridTableMessage( 
                                self, 
                                delmsg, 
                                new,    # position 
                                current-new, 
                        ) 
                        self.grid.ProcessTableMessage(msg) 
                elif new > current: 
                        msg = gridlib.GridTableMessage( 
                                self, 
                                addmsg, 
                                new-current 
                        ) 
                        self.grid.ProcessTableMessage(msg) 
        #print "Components in ResetView: \n%s \nself: %s \n****************\n" % (self.components, self)
        self.UpdateValues()
        self.grid.EndBatch()
        self.grid.Init()

    def UpdateValues( self ): 
        """Update all displayed values""" 
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES) 
        self.grid.ProcessTableMessage(msg)
        return
        self.grid.Init()
        for row in range(self.GetNumberRows()):
            for col in range(self.GetNumberCols()):
                attr = self.grid.GetOrCreateCellAttr(row, col)
                if row > len(self.components):
                    attr.SetReadOnly(1)
                    attr.SetBackgroundColour("light gray")
                else :
                    self.grid.GetOrCreateCellAttr(row, col).SetReadOnly(0)
                    attr.SetBackgroundColour("white")
                

    def GetColLabelValue(self, col):
        return self.colLabels[col]
    
    def GetRowLabelValue(self, col):
        return ""

    def SetGrid(self, grid):
        self.grid = grid

    def GetCellEditor(self, col):
        return self.cellEditors[col]

    def GetAsString(self):
        rows = self.GetNumberRows()
        cols = self.GetNumberCols()
        tableString = ""
        for row in range(rows):
            for col in range(cols):
                tableString += "%12s," % (self.GetValue(row,col))
            tableString += "\n"
        tableString += "\n"
        return tableString
    
    def GetAttr(self, row, col, someExtraParameter ):
        attr = self.grid.GetOrCreateCellAttr(row, col)
        attr.SetOverflow(False)
        return attr
    
#--------------------------------------------------------------------------------

class ReservoirDataTable(TrayDataTable):
    def __init__(self, data):
        self.GetComponentContainingItem = data.GetReservoir
        self.childString = "Component"
        self.childIDString = "SolID"
        TrayDataTable.__init__(self, data)
        self.colLabels = ["Reagent","Concentration","Unit","Remarks"]
        self.noRows = 10
        self.noCols = len(self.colLabels)
        self.cellEditors = [ReagentCellChoiceEditor(self.data, True),0,0,0]
        
    def GetValue(self, row, col):
        try:
            component = self.components[row][0]
        except IndexError:
            return ''
        #print component.PrettyPrint()
        reagent = self.data.GetReagent(component.GetProperty("SolID"))
        if reagent:
            if col == 0:
                return reagent.GetProperty("name")
            elif col == 2:
                return reagent.GetProperty("unit")
        else: return None
        if col == 1:
            conc = component.GetProperty("Concentration")
            for comp in self.components[row]:
                if comp.GetProperty("Concentration") != conc:
                    return ""
            return conc
        elif col == 3:
            rem = component.GetProperty("IngRemarks")
            for comp in self.components[row]:
                if comp.GetProperty("IngRemarks") != rem:
                    return ""
            return rem
        return ""

    def IsEmptyCell(self, row, col):
        try:
            component = self.components[row][0]
            return False
        except IndexError:
            return True

    def IsEditable(self, row, col):
        if row < len(self.components) + 2:
            return True
        else:
            return False

    def GetReagentNr(self, row, col):
        component = self.components[row][0]
        return component.GetProperty("SolID")

    def InitComponents(self):
        # Get all selected wells
        wells = self.data.GetActiveWells()
        #print "Wells: %s" % wells
        # Collect all the components and sort them into a 2D array
        # structure with idential ones forming an array in self.components.
        # self.componentSolIDs is used to preserve the order of the
        # components
        self.components = []
        self.componentIDs = []
        for well in wells:
            reservoir = self.GetComponentContainingItem(well)
            #print "Reservoir: %s"% reservoir
            if reservoir:
                #print reservoir.PrettyPrint()
                components = self.data.dbBackend.GetChildren(reservoir, self.childString)
                for component in components:
                    rID = component.GetProperty(self.childIDString)
                    #print "rID: %s" % rID
                    if not self.componentIDs.count(rID):
                        self.componentIDs.append(rID)
                        self.components.append([])
                    lPos = self.componentIDs.index(rID)
                    self.components[lPos].append(component)
        # Remove components that are not in all selected wells
        #print "1Components InitComps: \n%s" % self.components
        toBeRemoved = []
        for i,comps in enumerate(self.components):
            if len(comps) < len(wells):
                toBeRemoved.append(i)
        toBeRemoved.reverse()
        for i in toBeRemoved:
            self.components.pop(i)
            self.componentIDs.pop(i)
        #print "Components InitComps: \n%s" % self.components

    def SetValue(self, row, col, value):
        components = self.components[row]
        #print [c.GetProperty(self.childIDString) for c in components]
        if col == 0:
            # check if that reagents is already used in other components of the same reservoir
            alreadyExists = False
            for component in components:
                reservoirComponents = self.data.dbBackend.GetChildren(component.GetParent(),\
                    self.childString)
                for resComp in reservoirComponents:
                    if resComp.element is component.element:
                        continue
                    resCompID = resComp.GetProperty(self.childIDString)
                    if resCompID:
                        resCompID = int(resCompID)
                    if resCompID == value:
                        alreadyExists = True
            if alreadyExists:
                wx.MessageBox("Reagent is already used in one of the selected wells.\nPlease choose another one.", \
                "Message", wx.OK)
            else:
                for component in components:
                    component.SaveState(self.data.undoQueue)
                    component.SetProperty("SolID", value)
                self.data.SaveBackup()
        elif col == 1:
            for component in components:
                component.SaveState(self.data.undoQueue)
                component.SetProperty("Concentration", value)
            self.data.SaveBackup()
        elif col == 3:
            for component in components:
                component.SaveState(self.data.undoQueue)
                component.SetProperty("IngRemarks", value)
            self.data.SaveBackup()

#---------------------------------------------------------------------------

class ScreenSolutionDataTable(ReservoirDataTable):

    def __init__(self, data):
        ReservoirDataTable.__init__(self, data)
        self.GetComponentContainingItem = self.data.GetScreenSolution

#---------------------------------------------------------------------------

class DropDataTable(TrayDataTable):

    def __init__(self, data):
        self.colLabels = ["Description","Concentration","Volume","Buffer","Remarks"]
        self.childString = "DropComponent"
        self.childIDString = "Description"
        TrayDataTable.__init__(self, data)
        self.cellEditors = [0,0,0,0,0]
        
    def GetValue(self, row, col):
        if row == len(self.components):
            return ''
        component = self.components[row][0]
        value = component.GetProperty(self.colLabels[col])
        for comp in self.components[row]:
            if comp.GetProperty(self.colLabels[col]) != value:
                return ""
        return value

    def InitComponents(self):
        # Get all selected wells
        drops = self.data.GetActiveDrops()
        # Collect all the components and sort them into a 2D array
        # structure with idential ones forming an array in self.components.
        # self.componentSolIDs is used to preserve the order of the
        # components
        self.components = []
        self.componentIDs = []
        for drop in drops:
            drop = self.data.GetDrop(drop)
            if drop:
                components = self.data.dbBackend.GetChildren(drop, self.childString)
                for component in components:
                    rID = component.GetProperty(self.childIDString)
                    if not self.componentIDs.count(rID):
                        self.componentIDs.append(rID)
                        self.components.append([])
                    lPos = self.componentIDs.index(rID)
                    self.components[lPos].append(component)
        # Remove components that are not in all selected wells
        toBeRemoved = []
        for i,comps in enumerate(self.components):
            if len(comps) != len(drops):
                toBeRemoved.append(i)
        toBeRemoved.reverse()
        for i in toBeRemoved:
            self.components.pop(i)
            self.componentIDs.pop(i)

    def SetValue(self, row, col, value):
        if row == len(self.components):
            self.AppendRows()
        components = self.components[row]
        for component in components:
            component.SaveState(self.data.undoQueue)
            component.SetProperty(self.colLabels[col], value)
        self.data.SaveBackup()

    def AppendRows(self, numRows = 1):
        self.data.AddNewDropComponent()
        self.ResetView()

#---------------------------------------------------------------------------

class ReagentDataTable(TrayDataTable):

    def __init__(self, data):
        TrayDataTable.__init__(self, data)
        self.colLabels = ["Name","Conc.","Unit","Type","pH",\
                          "ion.str.","hydroph.","freq.",\
                          "[min]","[max]","Remarks"]
        self.fields = ["name","concentration","unit","type","ph",\
                          "ionicstrength","hydrophobicity","frequency",\
                          "minConc","maxConc","reagRemarks"]
        self.cellEditors = [0] * 11
        
    def DeleteRows(self, rows):
        print rows
        rows.reverse()
        for row in rows:
            del self.data.reagents[row]
        rows.reverse()
        TrayDataTable.DeleteRows(self, rows)
        self.data.UpdateEventListeners(["front","screen"], None)

    def GetValue(self, row, col):
        if row == len(self.components):
            return ''
        component = self.components[row][0]
        value = component.GetProperty(self.fields[col])
        return value

    def AppendRows(self, numRows = 1):
        self.data.AddNewReagent()
        self.ResetView()
        self.data.UpdateEventListeners(["front","screen"], None)

    def InitComponents(self):
        screen = self.data.GetScreen()
        reagents = self.data.GetReagents()
        #print "init: ", reagents
        self.components = []
        self.componentIDs = []
        for reag in reagents:
            rID = reag.GetProperty("name")
            #print "init: ", reag
            self.componentIDs.append(rID)
            c = [reag]
            self.components.append(c)

    def SetValue(self, row, col, value):
        if row == len(self.components):
            self.AppendRows()
        component = self.components[row][0]
        component.SaveState(self.data.undoQueue)
        component.SetProperty(self.fields[col], value)
        self.data.UpdateEventListeners(["front","screen"], None)
        self.data.SaveBackup()

#---------------------------------------------------------------------------


class trayGrid(gridlib.Grid):
    def __init__(self, parent, data, table, widths, *args, **kwds):
        gridlib.Grid.__init__(self, parent, -1, *args, **kwds)
        self.data = data
        table.SetGrid(self)
        self.SetTable(table, True)
        self.widths = widths
        self.colDragged = False
        self.SetRowLabelSize(10)
        self.SetMargins(0,0)
        self.SetColLabelSize(18)
        self.Init()
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnRightClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnDragColumnSize)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def Init(self):
        for c in range(self.GetNumberCols()):
            cellEditor = self.GetTable().GetCellEditor(c)
            if cellEditor:
                for r in range(self.GetNumberRows()):
                    editorInstance = cellEditor.Clone(self.data)
                    self.SetCellEditor(r,c,editorInstance)
                    #self.SetCellBackgroundColour(r, c, "white")


    def GetAsString(self):
        return self.GetTable().GetAsString()
    
    def OnAdd(self, event):
        self.AppendRows()
	if event: 
	    event.Skip()

    def OnDelete(self, event):
        if len(self.GetSelectionBlockTopLeft()):
            rows = range(self.GetSelectionBlockTopLeft()[0][0],self.GetSelectionBlockBottomRight()[0][0]+1)
        else:
            rows = self.GetSelectedRows()
        self.GetTable().DeleteRows(rows)
	if event:
	    event.Skip()

    def OnLabelLeftClick(self, event):
        col = event.GetCol()
        if col >= 0 and type(self.GetTable()) == ReagentDataTable:
            table = self.GetTable()
            label = table.GetColLabelValue(event.GetCol())
            index = table.colLabels.index(label)
            field = table.fields[index]
            self.data.SortReagents(field)
            self.OnDataChange()
            self.data.UpdateEventListeners(["front","screen"], None)
        
        event.Skip()

    def OnCellLeftClick(self,event):
        self.SetGridCursor(event.GetRow(), event.GetCol());
        self.GetCellEditor(event.GetRow(), event.GetCol()).position = \
            self.CellToRect(event.GetRow(), event.GetCol())
        self.EnableCellEditControl(True)
        event.Skip()
        
    def OnRightClick(self, event):
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnAdd, id=self.popupID1)
            self.popupID2 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnDelete, id=self.popupID2)
        # make a menu
        menu = wx.Menu()
        menu.Append(self.popupID1, "Add Component")
        if self.GetSelectedRows() or len(self.GetSelectionBlockTopLeft())==1:
            menu.Append(self.popupID2, "Delete Component")
        self.PopupMenu(menu, event.GetPosition())
        menu.Destroy()
        event.Skip()

    def OnSize(self, event):
        if not self.colDragged:
            width = self.GetSizeTuple()[0]
            for i,w in enumerate(self.widths):
                self.SetColSize(i, w * width)
        event.Skip(True)

    def OnDragColumnSize(self, event):
        self.colDragged = True
        event.Skip()
        
    def OnDataChange(self):
        if self.IsCellEditControlEnabled():
            self.SaveEditControlValue()
            self.EnableEditing(False)
        self.GetTable().ResetView()
        
        self.EnableEditing(True)

#---------------------------------------------------------------------------

class ReagentCellChoiceEditor(gridlib.PyGridCellEditor):

    def __init__(self, data, editable):
        gridlib.PyGridCellEditor.__init__(self)
        self.data = data
        self._editable = editable
#        self.Bind(wx.EVT_LEFT_DOWN, self.MouseChoice)
        self.Init()

    def __str__(self):
        return "My Class"

    def Init(self):
        self.reagents = self.data.GetReagents()
        self.reagentList = []
        self.reagentIdList = []
        for r in self.reagents:
            id = r.GetAttribute("id")
            self.reagentList.append(r.GetProperty("name"))
            self.reagentIdList.append(int(id))

    def Create(self, parent, id, evtHandler):
        #rect = parent.GetSelectedCells()[0].CellToRect
        self._tc = wx.Choice(parent, id, choices = self.reagentList,
                    pos = (self.position.x, self.position.y), 
                    size = (self.position.width, self.position.height))
        if len(self.reagentList):
            self._tc.SetSelection(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)


    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self._tc.SetDimensions(rect.x, rect.y, rect.width, rect.height,
                               wx.SIZE_ALLOW_MINUS_ONE)


    def MouseChoice(self, event):
        pass

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        """
        self.noSubmit = False
        try:
            self.startValue = grid.GetTable().GetReagentNr(row, col)
            self.startValue = self.reagentIdList.index(self.startValue)
            self._tc.SetStringSelection(self.reagentList[self.startValue])
        except IndexError:
            log.debug("Cannot find start Value for cell %s, %s", row, col)
            self.startValue = None
            self._tc.SetSelection(-1)
        self._tc.SetFocus()
        

    def EndEdit(self, row, col, grid, dummy):
        """
        Complete the editing of the current cell. Returns True if the value
        has changed.  If necessary, the control may be destroyed.
        """
        if self.noSubmit:
            return
        changed = False

        pclDescr = self._tc.GetStringSelection()
        # extract pcl

        pcl = ""
        try:
            pcl = self.reagentList.index(pclDescr)
            pcl = self.reagentIdList[pcl]
            if self.startValue == None:
                grid.GetTable().AppendRows()
        except KeyError:
            log.debug("Caught exception: Key %s not found", pclDescr)
        if pcl != self.startValue :
            changed = True
            grid.GetTable().SetValue(row, col, pcl) # update the table

        self.startValue = ''
        return changed


    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        """
        if self.startValue != None:
            self._tc.SetStringSelection(self.reagentList[self.startValue])
        else:
            self._tc.SetSelection(-1)
            self.noSubmit = True

    def Clone(self, data=None):
        """
        Create a new object which is the copy of this one
        """
        if not data: data = self.data
        return ReagentCellChoiceEditor(data, self._editable)


#---------------------------------------------------------------------------
#
#""" Test code
######################################################
#"""

#from dataStructures.elmtree_backend import OpenFile

#class TestFrame(wx.Frame):
#    def __init__(self):
#        wx.Frame.__init__(self, NULL, -1, "Double Buffered Test",
#                         wx.DefaultPosition,
#                         size=(500,200),
#                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)


#        data = OpenFile("../../files/screens/test_newformat.exp")
#        widths = [0.4, 0.2, 0.1, 0.3]
#        self.grid = trayGrid(self, data, widths)
#        self.grid.SetFocus()
#        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
#        sizer_1.Add(self.grid, 1, wx.EXPAND, 0)
#        self.SetSizer(sizer_1)


#class TrayApp(wx.App):
#    def OnInit(self):
#        wx.InitAllImageHandlers() # called so a PNG can be saved
#        frame = TestFrame()
#        frame.Show(True)

#        self.SetTopWindow(frame)

#        return True




#if __name__ == "__main__":
#    logging.basicConfig()
#    app = TrayApp(0)
#    app.MainLoop()
