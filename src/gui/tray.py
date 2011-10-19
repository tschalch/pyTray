#!/usr/bin/env python2.2

"""
The tray classes are providing the graphical interface to the wells and
drops of the crystallization experiment.

"""

import wx
from buffered_window import BufferedWindow
import logging
import sys
from util.trayErrors import NoObservationError, BurnInBackgroundError

log = logging.getLogger("tray")
log.setLevel(logging.WARN)

# constants for movement direction
MV_FORWARDS = 0
MV_BACKWARDS = 1
MV_UP = 2
MV_DOWN = 3

class Tray(BufferedWindow):
    def __init__(self, parent, data, screen = False, id = -1, style = wx.WANTS_CHARS):
        ## Any data the Draw() function needs must be initialized before
        ## calling BufferedWindow.__init__, as it will call the Draw
        ## function.
        
        self.data = data
        self.data.AddEventListener("front",self)
        self.data.AddEventListener("tray",self)
        self.keyListeners = []
        self.wells = {}
        self.drops = []
        self.noCols = data.noCols
        self.noRows = data.noRows
        self.noWells = self.noCols * self.noRows
        self.isScreen = screen
        self.activeDrop = None
        self.init()
        self.collectDrops()
        self.alphabet = {1:"A", 2:"B", 3:"C", 4:"D", 5:"E", 6:"F", 7:"G",\
                         8:"H", 9:"I", 10:"J", 11:"K", 12:"L", 13:"M", 14:"N",\
                         15:"O", 16:"P", 17:"Q", 18:"R", 19:"S", 20:"T", 21:"U",\
                         22:"V", 23:"W", 24:"X", 25:"Y", 26:"Z"}
        self.printInfo = 0
        if wx.Platform == '__WXGTK__':
            self.font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        else:
            self.font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)
        
        BufferedWindow.__init__(self, parent, id)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

    def AddKeyListener(self, newKeyListener):
        self.keyListeners.append(newKeyListener)
        
    def init(self):
        color = "grey"
        for i in range(self.noWells):
            self.wells[i] = Well(self.data, i,1,1,1,1, self.isScreen)

    def RefreshWells(self):
        for well in self.wells.values():
            well.Init()
            for drop in well.drops.values():
                drop.Init()

    def calcWells(self):
        """calculates well size"""
        (x,y) = self.GetSizeTuple()
        self.xoffset = 0
        
        if x/(self.noCols + 2) > y/(self.noRows + 2):
            self.boxwidth = y/(self.noRows + 2)
            self.xoffset = (x - ((self.noCols + 2) * self.boxwidth)) / 2
        else:
            self.boxwidth = x/(self.noCols + 2)
        
        self.boxpitch = self.boxwidth + 2

        self.border = self.boxwidth
        newFont = 10
        if self.boxwidth < 20:
            newFont = self.boxwidth / 2.
        self.font = wx.Font(newFont, wx.MODERN, wx.NORMAL, wx.NORMAL)
        
        for i in range(self.noWells):
            rect = self.wells[i]
            c = i % self.noCols
            r = int(i/self.noCols)
            rect.SetX(c * self.boxpitch + self.border + self.xoffset)
            rect.SetY(r * self.boxpitch + self.border)
            rect.SetWidth(self.boxwidth)
            rect.SetHeight(self.boxwidth)


    def collectDrops(self):
        del self.drops[:]
        for i in range(self.noWells):
            drops = self.wells[i].drops
            for drop in drops.values():
                self.drops.append(drop)


    def OnSize(self, event):
        self.Width, self.Height = self.GetClientSizeTuple()
        self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
        dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        self.DrawBackground(dc)
        self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
        self.UpdateDrawing()

        
    def Draw(self, dc):
        dc.BeginDrawing()
        dc.Clear() # make sure you clear the bitmap!
        dc.DrawBitmap(self.bgImage.ConvertToBitmap(), 0,0,)
        for well in self.wells.values():
            try:
                well.Draw(dc)
            except BurnInBackgroundError, e:
                #dc.EndDrawing()
                self.BurnIntoBackground([e.caller.dropNr])
                well.Draw(dc)
                #self.Draw(dc)
        dc.EndDrawing()
        

    def DrawBackground(self, dc):
        self.calcWells()
        dc.BeginDrawing()
        dc.SetBackground( wx.Brush("White"))
        dc.SetFont(self.font)
        dc.Clear() # make sure you clear the bitmap!

        # Here's the actual drawing code.
        colNrY = 0.5 * self.border
        rowNrX = self.xoffset + int(round(0.5 * self.boxpitch))
        for pos in self.wells.keys():
            c = pos % self.noCols
            r = int(pos/self.noCols)
            colNrX = self.xoffset + self.border + int(round((c + 0.3) * self.boxpitch))
            dc.DrawText(str(c + 1), colNrX, colNrY)
            rowNrY = self.border + int(round((r + 0.25) * self.boxpitch))
            dc.DrawText(self.alphabet[r + 1], rowNrX, rowNrY)
            
        for well in self.wells.values():
                #dc.SetBrush(wx.Brush(well.GetColor(),wx.SOLID))
                #dc.DrawRectangle(well.GetX(), well.GetY(), \
                #                 well.GetWidth(), well.GetHeight())
            try:
                well.Draw(dc, True)
            except BurnInBackgroundError, e:
                well.Draw(dc, True)

        if self.printInfo:
            font = wx.Font(self.boxwidth/5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,\
                           wx.FONTWEIGHT_NORMAL)
            dc.SetFont(font)
            filename = self.data.GetFilename()
            date = self.data.observationDate
            dc.DrawText("File: " + filename, self.border,\
                        self.boxpitch * self.noRows + 1.0 * self.border)
            if date:
                dc.DrawText("Observation: " + date, self.border,\
                           self.boxpitch * self.noRows + 1.3 * self.border)

        dc.EndDrawing()
        self.bgImage = self._Buffer.ConvertToImage()


    def GetImage(self, size):
        # use a new dc to print tray and date and filename
        self.printInfo = 1
        oldSize = self.GetSizeTuple()
        newSize = size
        self.SetSize(newSize)
        dc = wx.MemoryDC()
        buffer = wx.EmptyBitmap(self.Width, self.Height)
        dc.SelectObject(buffer)
        self.DrawBackground(dc)
        self.printInfo = 0
        self.SetSize(oldSize)
        return buffer

    def OnCopy(self, event):
        # copy buffer to clipboard
        clipdata = wx.BitmapDataObject()
        clipdata.SetBitmap(self.GetImage(self.GetSize()))
        wx.TheClipboard.Open() 
        wx.TheClipboard.SetData(clipdata) 
        wx.TheClipboard.Close()

    def OnMultiply(self, event):
        try:
            factor = float(wx.GetTextFromUser("Please enter multipllication factor",\
                                   "Multiplication factor"))
        except ValueError:
            log.debug("Could not convert to float.")
            factor = 0
        if self.isScreen and factor:
            self.data.MultiplyScreenSolutions(factor)
            self.data.UpdateEventListeners(["screen"],self)
        elif not self.isScreen and factor:
            self.data.MultiplyReservoirSolutions(factor)
            self.data.UpdateEventListeners(["front"],self)


    def OnRightClick(self, event):
        # only do this part the first time so the events are only bound once
        #
        # Yet another anternate way to do IDs. Some prefer them up top to
        # avoid clutter, some prefer them close to the object of interest
        # for clarity. 
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnCopy, id=self.popupID1)
            self.popupID2 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnMultiply, id=self.popupID2)
            
        # make a menu
        menu = wx.Menu()
        menu.Append(self.popupID1, "Copy Graphics")
        menu.Append(self.popupID2, "Multiply Well Concentrations")
        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu, event.GetPosition())
        menu.Destroy()

    def ClearWells(self):
        for well in self.wells.values():
            well.Toggle(-1)
            well.ClearDrops()

    def OnClick(self, event):
        if not event.m_controlDown:
            self.ClearWells()

        mp = event.GetPosition()
        (x,y) = event.GetPosition()
        dx = x - self.border -  self.xoffset
        dy = y - self.border
        col = dx / self.boxpitch
        row = dy / self.boxpitch
        position = row * self.noCols + col
        self.activeWell = (position)

        if dx < 0 and  dy < 0:
            for well in self.wells.values():
                if event.m_shiftDown or self.isScreen:
                    well.Toggle()
                else:
                    well.ToggleDrop(well.GetPosition())
            self.data.UpdateEventListeners(["front","screen"],self)
            return
            
        if dx < 0:
            for key,well in self.wells.items():
                if int(key/self.noCols) == row:
                    if event.m_shiftDown or self.isScreen:
                        well.Toggle()
                    else:
                        well.ToggleDrop(well.GetPosition())
            self.data.UpdateEventListeners(["front","screen"],self)
            return

        if dy < 0:
            if event.m_shiftDown or self.isScreen:
                for key,well in self.wells.items():
                    if key % self.noCols == col:
                        well.Toggle()
            else:
                counter = 0
                for drop in self.drops:
                    dropy = drop.GetY()
                    if drop.Inside((x,dropy)):
                        drop.Toggle()
            self.data.UpdateEventListeners(["front","screen"],self)
            return

        if col < self.noCols and row < self.noRows:
            self.wells[position].ToggleDrop(mp)
        self.data.UpdateEventListeners(["front","screen"],self)


    def Move(self, direction):

        # get active drops or reservoir
        try:
            activeDrop = self.data.GetActiveDrops()[0]
        except IndexError:
            activeDrop = None
        try:
            activeReservoir = self.data.GetActiveReservoirs()[0]
        except IndexError:
            activeReservoir = None

        # initialize parameters for calculation of next position
        if activeDrop:
            id = self.data.noDrops * activeDrop[0] + activeDrop[1]
            containers = self.drops
            total = len(self.drops)
            nrDrops = self.data.GetNrDrops()
            drop = True
        elif activeReservoir is not None:
            id = activeReservoir
            total = self.noWells
            containers = self.wells
            nrDrops = 1
            drop = False
        else:
            return

        # calculate next position depending on direction
        if direction == MV_FORWARDS:
            next = (id + 1) % total
        elif direction == MV_BACKWARDS:
            next = (id + total - 1) % total
        elif direction == MV_UP:
            next = (id - (self.noCols * nrDrops) + \
                        total )  % total
        elif direction == MV_DOWN:
            next = (id + (self.noCols * nrDrops))\
                       % total

        # set selection on next position
        self.ClearWells()
        containers[next].Toggle(1)
        self.data.UpdateEventListeners(["front","screen"],self)

    def OnKey(self, event):
        # Send key event to listeners, register successful change
        update = False
        for keyListener in self.keyListeners:
            if keyListener.OnKey(event):
                update = True
        if update:
            self.data.UpdateEventListeners(["front","screen"],self)
        drops = self.data.GetActiveDrops()
        if len(drops):
            self.activeDrop = drops[0]

        forwardKeys = [wx.WXK_RIGHT, wx.WXK_TAB, wx.WXK_NUMPAD_ENTER,
                       wx.WXK_RETURN]
        if forwardKeys.count(event.GetKeyCode()):
            self.Move(MV_FORWARDS)

        if event.GetKeyCode() == wx.WXK_LEFT:
            self.Move(MV_BACKWARDS)

        if event.GetKeyCode() == wx.WXK_UP:
            self.Move(MV_UP)
            
        if event.GetKeyCode() == wx.WXK_DOWN:
            self.Move(MV_DOWN)

        try:
            keyEvents = {wx.WXK_NUMPAD0:0,wx.WXK_NUMPAD1:1,wx.WXK_NUMPAD2:2,wx.WXK_NUMPAD3:3,wx.WXK_NUMPAD4:4, 
                         wx.WXK_NUMPAD5:5,wx.WXK_NUMPAD6:6,wx.WXK_NUMPAD7:7,wx.WXK_NUMPAD8:8,wx.WXK_NUMPAD9:9,
                         48:0, 49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7, 56:8, 57:9, wx.WXK_NUMPAD_SUBTRACT:-1,
                         wx.WXK_SUBTRACT:-1, 45:-1} 
            keyCode = event.GetKeyCode()
            if keyEvents.has_key(keyCode):
                self.data.SetScore(keyEvents[keyCode])
                self.BurnIntoBackground(drops)
            if len(drops) == 1 and keyEvents.has_key(keyCode):
                self.Move(MV_FORWARDS)
        except NoObservationError, e:
            d = wx.MessageBox("Please enter observation date first.",\
                         "Error", wx.OK, self)

    def BurnIntoBackground(self, drops):
        buffer = wx.EmptyBitmap(self.Width, self.Height)
        dc = wx.BufferedDC(wx.ClientDC(self), buffer)
        dc.BeginDrawing()
        dc.Clear() # make sure you clear the bitmap!
        dc.DrawBitmap(self.bgImage.ConvertToBitmap(), 0,0,)
        for drop in drops:
            id = self.data.noDrops * drop[0] + drop[1]
            self.drops[id].Draw(dc, True)
        dc.EndDrawing()
        self.bgImage = buffer.ConvertToImage()

    def OnDataChange(self):
        self.UpdateDrawing()
            

class Well(wx.Rect):
    """ Class handling the properties of the well in a graphics tray"""
    border = 2
    onColor = 'yellow'
    offColor = 'grey'
    
    def __init__(self, data, wellNr, x=0, y=0, width=0, height=0, screen = False):
        wx.Rect.__init__(self, x, y, width, height)
        self.wellNr = wellNr
        self.data = data
        self.nrDrops = self.data.GetNrDrops()
        self.drops = {}
        self.color = self.offColor
        self.isScreen = screen
        #self.needsUpdate = True
        for i in range(self.nrDrops):
            pos = (wellNr, i)
            self.drops[i] = Drop(data, pos)
        self.Init()


    def Init(self):
        self.container = self.data.GetReservoir(self.wellNr)
        

    def calcDrops(self):
        """calculates drop size"""
        height = (self.height - 2 * self.border) / 2
        width = int((self.width - 2 * self.border) * 1.0 / self.nrDrops)
        for i, drop in self.drops.items():
            drop.SetX(self.x + width * (i) + self.border)
            drop.SetY(self.y +  self.border)
            drop.SetWidth(width)
            drop.SetHeight(height)

    def Draw(self, dc, background = False):
        if self.container.selected or background:
            if background:
                dc.SetBrush(wx.Brush(self.offColor,wx.SOLID))
            else:
                dc.SetBrush(wx.Brush(self.GetColor(),wx.SOLID))
            dc.DrawRectangle(self.GetX(), self.GetY(), \
                             self.GetWidth(), self.GetHeight())
        if self.nrDrops and not self.isScreen:
            if background:
                self.calcDrops()
            for drop in self.drops.values():
                if self.container.selected and not drop.container.selected:
                    try:
                        drop.Draw(dc, True)
                    except BurnInBackgroundError, e:
                        raise
                        #raise BurnInBackgroundError(e.caller)
                else:
                    try:
                        drop.Draw(dc, background)
                    except BurnInBackgroundError:
                        raise
        #if not self.container.selected:
        #    self.isChanged = False

        

    def GetColor(self):
        """ returns well color """
        dropSelected = False
        if type(self) == Well and self.isScreen:
            for drop in self.drops.values():
                if drop.container.selected:
                    dropSelected = True
        if self.container.selected or dropSelected:
            return wx.NamedColor(self.onColor)
        else:
            return wx.NamedColor(self.offColor)

    def SetColor(self, color):
        """ sets Well color """
        self.color = color

    def ClearDrops(self):
        for drop in self.drops.values():
            drop.Toggle(-1)
        
        
    def ToggleDrop(self, point, state = 0):
        if point.x == self.x and point.y == self.y:
            for drop in self.drops.values():
                drop.Toggle(state)
            return

        found = 0
        if self.nrDrops:
            for drop in self.drops.values():
                if drop.Inside(point):
                    drop.Toggle(state)
                    found = 1
            if not found:
                self.Toggle(state)
        else:
            self.Toggle(state)

    def Toggle(self, state = 0):
        #oldSelection = self.container.selected
        if state == 0:
##            if self.color == self.offColor:
##                self.color = self.onColor
##            else:
##                self.color = self.offColor
            #self.Init()
            self.container.selected = not self.container.selected
        elif state == 1:
##            self.color = self.onColor
            #self.Init()
            self.container.selected = True
        else:
##            self.color = self.offColor
            self.container.selected = False
        #if oldSelection != self.container.selected:
        #    self.isChanged = True


class Drop(Well):
    def __init__(self, data, dropNr, x=0, y=0, width=0, height=0):
        """ data is a TrayData object and dropNr is a tuple (wellposition, dropNr)"""
        wx.Rect.__init__(self, x, y, width, height)
        self.color = self.offColor
        self.data = data
        self.dropNr = dropNr
        self.hasImage = False
        #self.isChanged = True
        self.Init()

    def Draw(self, dc, background = False):
        if self.container.selected or background:
            if background:
                dc.SetBrush(wx.Brush(self.GetColor(True),wx.SOLID))
            else:
                dc.SetBrush(wx.Brush(self.GetColor(),wx.SOLID))
            dc.DrawRectangle(self.GetX(), self.GetY(), self.GetWidth(),\
                                     self.GetHeight())
            if self.HasImages():
                if not self.hasImage:
                    self.hasImage = True
                    #raise BurnInBackgroundError("New image update detected", self)
                dc.SetBrush(wx.Brush(wx.NamedColor("white"),wx.SOLID))
                boxsize = 0
                if self.GetWidth() > self.GetHeight():
                    boxsize =  round(self.GetHeight()/3)
                else:
                    boxsize =  round(self.GetWidth()/3)
                dc.DrawRectangle(self.GetX(), self.GetY(), boxsize,\
                                 boxsize)        
            #if not self.container.selected:
            #    self.isChanged = False

    def Init(self):
        self.container = self.data.GetDrop(self.dropNr)
        
    def HasImages(self):
        images = self.data.GetImages(0, self.dropNr)
        return len(images)

    def GetColor(self, background = False):
        if (self.data.GetObservation(0, self.dropNr) and not self.container.selected) \
            or ( self.data.GetObservation(0, self.dropNr) and background):
            try:
                score = self.data.GetObservation(0, self.dropNr).GetProperty("ScoreValue")
                log.debug("Score: %s", score)
                return "#" + self.data.GetScoreColor(score)
            except ValueError:
                return wx.NamedColor(self.offColor)
            except KeyError:
                log.debug("ScoreColor %s not found", score)
                return wx.NamedColor(self.offColor)
        else:
            return Well.GetColor(self)
    
    
    

"""
Testing code
###################################3
"""

import controller

class GuiApp(wx.App):

    def OnInit(self):
        self.controller = controller.Controller(["U:/Personal/Programming/pyTray/src/","\\\\xtend\\biopshare/Thomas/Screens/pyTray_Files/test.exp"], self)
        frame = wx.Frame(None)
        data = self.controller.GetTrayData(frame, "\\\\xtend\\biopshare/Thomas/Screens/pyTray_Files/test.exp")
        tray = Tray(frame,data)
        frame.Show()
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
