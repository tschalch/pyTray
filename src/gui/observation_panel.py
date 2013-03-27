import wx, os
import logging, pdb
logging.basicConfig()
log = logging.getLogger("observation_panel")
#from video_frame import VideoFrame
video = False
if video:
    from util.twain_camera import TwainCamera

from PIL import Image
#Image._initialized=2
from util.trayErrors import NoZipFileError
from buffered_window import BufferedWindow
import os, sys

img_wildcard = "JPG Files (*.jpg)|*.jpg|"    \
           "All files (*.*)|*.*"

CAMERA = 1   #1=twain, 2=microsoft driver

class ObservationPanel(wx.Panel):
    """
    GUI component that displays and handles the observations
    made on a particular experiment
    data = tray_data derived object
    """

    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.videoFrame = 0
        self.data = data
        self.images = []
        self.data.AddEventListener("front",self)
        self.camera = None
        
        self.Init()
        self.obsText = wx.StaticText(self, -1, "Observation:")
        self.obsText.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.date_combo = wx.ComboBox(self, -1, choices=self.dates, \
                                     style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.add_obs_button = wx.Button(self, -1, "Add new", 
                                        size=wx.Size(-1, self.date_combo.GetSize()[1]))
        self.ren_obs_button = wx.Button(self, -1, "Rename", 
                                        size=wx.Size(-1, self.date_combo.GetSize()[1]))
        self.del_obs_button = wx.Button(self, -1, "Delete", 
                                        size=wx.Size(-1, self.date_combo.GetSize()[1]))
        self.line = wx.StaticLine(self, -1)
        self.line2 = wx.StaticLine(self, -1)
        # detail panel controls
        self.score_combo = wx.ComboBox(self, -1, choices=self.choices, \
                                      style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.remark_box = wx.TextCtrl(self, -1, "", size=wx.Size(self.score_combo.GetSize()[0],120), style=\
                          wx.TE_MULTILINE|wx.TE_RICH)
        self.imagePanel = wx.Notebook(self, -1, self.data.IMAGE_SIZE, style=wx.NB_LEFT)
        self.addImageButton = wx.Button(self, -1, "Add Image File")

        self.detailControls = [self.score_combo,self.remark_box,self.imagePanel,
                               self.addImageButton]

        if video:
            self.videoButton = wx.Button(self, -1, "Start Video")
            self.videoGrabButton = wx.Button(self, -1, "Grab Image")
            self.detailControls.extend([self.videoButton, self.videoGrabButton])
            self.Bind(wx.EVT_BUTTON, self.StartVideo, self.videoButton)
            self.Bind(wx.EVT_BUTTON, self.OnGrabImage, self.videoGrabButton)

        self.Bind(wx.EVT_TEXT, self.SetRemarks, self.remark_box)
        self.Bind(wx.EVT_COMBOBOX, self.SetDate, self.date_combo)
        self.Bind(wx.EVT_COMBOBOX, self.SetScore, self.score_combo)
        self.Bind(wx.EVT_BUTTON, self.AddObservation, self.add_obs_button)
        self.Bind(wx.EVT_BUTTON, self.RenameObservation, self.ren_obs_button)
        self.Bind(wx.EVT_BUTTON, self.DeleteObservation, self.del_obs_button)
        self.Bind(wx.EVT_BUTTON, self.OnAddImage, self.addImageButton)

        #self.__set_properties()
        self.__do_layout()
        #self.Update()
        # On start show the latest observation
        if len(self.dates):
            self.date_combo.SetValue(self.dates[-1])
            self.SetDate(wx.EVT_COMBOBOX)

    def __set_properties(self):
        # begin wx.Glade: MyFrame.__set_properties
        self.date_combo.SetSelection(0)
        self.date_combo.Refresh()
        self.SetDate(wx.EVT_COMBOBOX)
        self.observationDate = self.date_combo.GetValue()
        if video:
            self.videoGrabButton.Disable()
        # end wx.Glade

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        observations_sizer = wx.BoxSizer(wx.HORIZONTAL)
        observations_sizer.Add(self.obsText, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        observations_sizer.Add(self.date_combo, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        observations_sizer.Add(self.add_obs_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        observations_sizer.Add(self.ren_obs_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        observations_sizer.Add(self.del_obs_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)

        main_sizer.Add(observations_sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.line, 0, wx.EXPAND, 0)

        details_sizer = wx.FlexGridSizer(1, 2, 0, 10)
        details_left_sizer = wx.BoxSizer(wx.VERTICAL)
        details_left_sizer.Add(self.score_combo, 0, 0, 0)
        details_left_sizer.Add(self.remark_box, 0, 0, 0)
        if video:
            details_left_sizer.Add(self.videoButton, 0, wx.TOP, 5)
            details_left_sizer.Add(self.videoGrabButton, 0, wx.TOP, 5)
        details_left_sizer.Add(self.addImageButton, 0, wx.TOP, 5)
        details_sizer.Add(details_left_sizer, 0, wx.EXPAND, 0)
        details_sizer.Add(self.imagePanel, 0, 0, 0)
        main_sizer.Add(details_sizer, 0, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        main_sizer.SetSizeHints(self.parent)


    def OnAddImage(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=img_wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()
	    for f in paths:
		self.AddImage(f)
        dlg.Destroy()

    def AddImage(self, imgfile):
        try:
            self.data.AddImage(os.path.abspath(imgfile))
            self.data.UpdateEventListeners(["front", "tray"],self)
        except NoZipFileError:
            d = wx.MessageBox("You need to save your file before you can add images.",\
                 "Warning", wx.OK, self)
            return
        

    def AddObservation(self, event, date=None):
        if not date:
            date = wx.GetTextFromUser("Please enter an observation date", "New Observation")
        if date:
            self.data.AddNewObservation(date)
            self.date_combo.Append(date)
            self.date_combo.SetValue(date)
            self.dates.append(date)
            self.SetDate(wx.KeyEvent())
            self.data.UpdateEventListeners(["front"],self.add_obs_button)

    def RenameObservation(self, event):
        text = wx.GetTextFromUser("Please enter new observation name", 
                                 "Rename Observation", self.observationDate)
        if text and text != self.observationDate:
            self.data.RenameObservation(self.observationDate, text)
            pos = self.date_combo.FindString(self.observationDate)
            self.date_combo.Delete(pos)
            self.date_combo.Insert(text, pos)
            self.date_combo.SetValue(text)
            self.SetDate(wx.KeyEvent())
            self.data.UpdateEventListeners(["front"],self.ren_obs_button)

    def DeleteObservation(self, event, interactive=True):
        if interactive:
            answer = wx.MessageBox("Do you really want to delete the entire observation?", \
                "Confirmation", wx.YES_NO)
        else:
            answer = wx.YES
        if answer == wx.YES:
            self.data.DeleteObservation(self.observationDate)
            pos = self.date_combo.FindString(self.observationDate)
            self.date_combo.Delete(pos)
            del self.dates[pos]
            if len(self.dates):
                self.date_combo.SetValue(self.dates[-1])
                self.SetDate(None)
            self.data.UpdateEventListeners(["front"],self.GetParent())
        pass

    def GrabImage(self):
        if CAMERA == 1 and self.camera:
            #img = self.camera.GetImage()
            self.camera.ProcessXFer(None)
            
        if self.videoFrame:
            img = self.videoFrame.GetImage()
            #draw = ImageDraw.Draw(img)
            drops = self.data.GetActiveDrops()
            if len(drops) == 1:
                position = drops[0]
                try:
                    self.data.AddImage(img)
                except NoZipFileError:
                    d = wx.MessageBox("You need to save your file before you can add images.",\
                         "Warning", wx.OK, self)
                    return
            self.Update()
        else:
            log.warn("Video not running")

    def Init(self):
        self.video = False
        self.InitScores()
        dates = self.data.GetObservationDates()
        self.dates = []
        for date in dates:
            self.dates.append(date)
        pass

    def InitScores(self):
        scores = self.data.GetScores()
        self.choices = []
        self.scores = {}
        for key,score in scores.items():
            self.choices.append(str(score.GetProperty("ScoreNr")) + " " + score.GetProperty("ScoreText"))
            self.scores[score.GetProperty("ScoreNr")] = score.GetProperty("ScoreText")

    def OnDataChange(self):
        self.images = []
        self.Update()
        pass

    def OnGrabImage(self, event):
        self.GrabImage()
        self.data.UpdateEventListeners(["front"],self.videoGrabButton)

    def OnKey(self, event):
        if event.GetKeyCode() == 73:
            self.GrabImage()
            return True

    def SetDate(self, event):
        self.observationDate = self.date_combo.GetValue()
        self.data.SetObservationDate(self.observationDate)
        self.data.UpdateEventListeners(["front", "tray"],self)

    def SetScore(self, event):
        score = self.score_combo.GetValue().split()[0]
        self.data.SetScore(int(score))
        self.data.UpdateEventListeners(["front", "tray"],self)

    def SetRemarks(self, event):
        remark = self.remark_box.GetValue()
        self.data.SetObservationRemarks(remark)

    def StartVideo(self, event):
        if CAMERA == 1:
            USE_CALLBACK=True
            if not self.camera:
                self.camera = TwainCamera(self)
            self.camera.OpenScanner(self.GetHandle(),
                        ProductName="Crystal camera", UseCallback=USE_CALLBACK)
            self.camera.AcquireNatively()
            self.video = True
            return
        self.videoFrame = VideoFrame(self)
        self.videoFrame.SetSize((600,500))
        self.videoFrame.Show()
        self.video = True
        self.Update()
        self.videoFrame.SetFocus()

    def StopVideo(self):
        self.video = False
        self.Update()

    def Update(self):
        drops = self.data.GetActiveDrops()
        self.InitScores()
        self.score_combo.Clear()
        for choice in self.choices:
            self.score_combo.Append(choice)
        self.score_combo.SetSelection(-1)
        self.Images = []
        if len(drops) == 1:
            for control in self.detailControls:
                control.Enable()
            if self.video:
                if self.camera.AcquirePending:
                    self.videoButton.Disable()
                    self.videoGrabButton.Enable()
                else:
                    self.videoButton.Enable()
                    self.videoGrabButton.Disable()

            position = drops[0]
            if self.observationDate:
                self.observation = self.data.GetObservation(self.observationDate,position)
                try:
                    scoreValue = self.observation.GetProperty("ScoreValue")
                    score = str(scoreValue) + " " + \
                            self.scores[self.observation.GetProperty("ScoreValue")]
                    self.score_combo.SetValue(score)
                except ValueError:
                    self.score_combo.SetSelection(-1)
                except KeyError:
                    log.debug("ScoreValue of %d not found in self.scores", scoreValue)
                    self.score_combo.SetSelection(-1)
                except AttributeError:
                    log.debug("No Observation found")
                    return
                remarks = self.observation.GetProperty("ObservationRemarks")
                self.remark_box.SetValue(remarks)
                self.images = self.data.GetImages(self.observationDate,position)
                #self.__do_layout()
            elif len(drops) == 0:
                self.remark_box.Clear()
                for control in self.detailControls:
                    control.Disable()
                    pass

        if len(self.images) == 0:
	    self.imagePanel.Disable()
	    panel = wx.Panel(self.imagePanel, -1, wx.DefaultPosition, self.data.IMAGE_SIZE)
	    self.imagePanel.DeleteAllPages()
	    self.imagePanel.AddPage(panel, "0")
        else:
            #self.imagePanel.Show(0)
            self.imagePanel.DeleteAllPages()
            for i,img in enumerate(self.images):
		obs_panel = ObsImagePanel(self.imagePanel,img, self.data, self.data.IMAGE_SIZE)
                self.imagePanel.AddPage(obs_panel, str(i+1))
		obs_panel.Resize()
            #self.imagePanel.Enable()
	    #pdb.set_trace()
            #self.imagePanel.Show(1)
        

class ImagePanel(BufferedWindow):
    """
    Parameter img: PIL image
    """
    def __init__(self, parent, img, imgSize, id = -1):
        self.image = img
        self.imageSize = imgSize
        BufferedWindow.__init__(self, parent, id, wx.DefaultPosition, imgSize)

    def Draw(self, dc):
        self.showImage = self.Resize()
        imgSize = self.showImage.size
        image = wx.EmptyImage(imgSize[0], imgSize[1])
        image.SetData(self.showImage.convert("RGB").tostring())
        bitmap = image.ConvertToBitmap()
        dc.DrawBitmap(bitmap,0,0)

    def Resize(self):
        iw,ih = self.image.size
        iar = float(iw)/ih  # image aspect ratio
        pw,ph = self.imageSize
        par = float(pw)/ph
        if iar > par:
            scale = float(pw)/iw
            newSize = (int(scale * self.image.size[0]),int(scale * self.image.size[1]))
        else:
            scale = float(ph)/ih
            newSize = (int(scale * self.image.size[0]),int(scale * self.image.size[1]))
        return self.image.resize(newSize, Image.ANTIALIAS)
    

class ObsImagePanel(ImagePanel):
    """
    Class used for image display in the observation panel
    img = DOM image Element
    imgSize = size tuple
    """

    def __init__(self, parent, img, data, imgSize, id = -1):
        self.img = img
        self.data = data
        self.Init()
        ImagePanel.__init__(self, parent, self.image, imgSize)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
	self.Layout()

    def Init(self):
        if self.img.GetText():
            self.image = Image.open(self.data.dbBackend\
                                    .GetImage("tb_" + self.img.GetText()))

    def OnRightClick(self, event):
        # only do this part the first time so the events are only bound once
        #
        # Yet another anternate way to do IDs. Some prefer them up top to
        # avoid clutter, some prefer them close to the object of interest
        # for clarity. 
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnDelete, id=self.popupID1)
            self.popupID2 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnOpen, id=self.popupID2)
            self.popupID3 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnAddImage, id=self.popupID3)
            
        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID2, "Open")
        menu.Append(self.popupID3, "Add New Image")
        menu.Append(self.popupID1, "Delete")
        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu, event.GetPosition())
        menu.Destroy()
        
    def OnDelete(self, event):
        answer = wx.MessageBox("Do you really want to delete this image?", \
            "Confirmation", wx.YES_NO)
        if answer == wx.YES:
            self.data.DeleteImage(self.img)
            self.data.UpdateEventListeners(["front"],self.GetParent())

    def OnOpen(self, event):
        self.data.OpenImage(self.img)

    def OnAddImage(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=img_wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPaths()
            file = dlg.GetFilename()
            self.data.AddImage(file)
            self.data.UpdateEventListeners(["front", "tray"],self.GetParent())
        dlg.Destroy()

"""
Testing code
###################################3
"""

import controller

class GuiApp(wx.App):

    def OnInit(self):
        self.controller = controller.Controller(["U:/Personal/Programming/pyTray/src/","V:/Thomas/Screens/pyTray_Files/test.exp"], self)
        self.frame = wx.Frame(None, -1, "Observation Panel Test")
        #self.controller.data.drops[(7,0)].selected = True
        self.panel = ObservationPanel(self.frame, self.controller.data)
        self.frame.Show(True)
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

        
