#!/usr/bin/env python


import wx
from lib.videocapture.VideoCapture import Device
from PIL import Image, ImageOps
import time
from buffered_window import BufferedWindow
import os.path

class VideoWindow(BufferedWindow):
    def __init__(self, parent, cam, id = -1):
        ## The videocapture camera device
        self.parent = parent
        self.cam = cam
        self.aspectRatio = float(self.cam.getImage().size[0])/self.cam.getImage().size[1]
        BufferedWindow.__init__(self, parent, id)
        self.UpdateDrawing()
        self.SetSize(self.cam.getImage().size)

    def Draw(self, dc):
        ## Gets the image from the camera and feeds it into the dc
        dc.Clear()
        source = self.cam.getImage()
        source = source.resize((self.Width, self.Height), Image.NEAREST)
        source = ImageOps.autocontrast(source,0.0)
        self.image = wx.EmptyImage(source.size[0],source.size[1])
        self.image.SetData(source.convert("RGB").tostring())
        bitmap = self.image.ConvertToBitmap()
        dc.DrawBitmap(bitmap,0,0)

    def OnSize(self, event):
        BufferedWindow.OnSize(self, event)
        if float(self.Width) / self.Height > self.aspectRatio:
            self.Width = int(round(self.Height * self.aspectRatio))
        elif float(self.Width) / self.Height < self.aspectRatio:
            self.Height = int(round(self.Width / self.aspectRatio))

        
    def GetImage(self):
        imgs = []
        averages = 1
        for i in range(averages):
            time.sleep(0.01)
            imgs.append(self.cam.getImage())
            
        while len(imgs) > 1:
            imgs = self.average(imgs)
        return ImageOps.autocontrast(imgs[0], 0.0)

    def average(self,imgs):
        avgs = []
        for i in range(len(imgs) / 2):
            avgs.append(Image.composite(imgs[i], imgs[i+1],None))
        return  avgs

class VideoFrame(wx.Frame):
    def __init__(self, parent, id = -1):
        wx.Frame.__init__(self, parent, id, "Video Frame",
                         wx.DefaultPosition,
                         size=(-1,-1),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        """
        The video is run as a background task by activating it when
        the frame sends an idle event.
        """

        ## setup the menu bar
        """
        MenuBar = wx.MenuBar()
        file_menu = wx.Menu()
        ID_EXIT_MENU = wx.NewId()
        file_menu.Append(ID_EXIT_MENU, "E&xit","Terminate the program")
        EVT_MENU(self, ID_EXIT_MENU, self.OnQuit)
        ID_SETTIINGS_MENU = wx.NewId()
        file_menu.Append(ID_SETTIINGS_MENU, "Video Settings","Set the video properties")
        EVT_MENU(self, ID_SETTIINGS_MENU, self.OnSettings)
        MenuBar.Append(file_menu, "&File")
        self.SetMenuBar(MenuBar)
        """

        self.observationPanel = parent
        ## setup the video camera
        try:
            self.cam = Device(devnum=0, showVideoWindow=0)       
        except:
            self.cam = DummyCam()
        self.video = VideoWindow(self, self.cam)
        self.running = 1
        self.Fit()
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        if self.observationPanel:
            self.Bind(wx.EVT_CLOSE, self.OnExit)

    def OnQuit(self,event):
        self.Close(true)

    def OnExit(self, event):
        self.observationPanel.StopVideo()
        self.Destroy()

    def OnSettings(self, event):
        self.cam.displayCaptureFilterProperties()
        
    def OnIdle(self,event):
        self.video.UpdateDrawing()
        ## 25 ms seems to be a good compromise between responsiveness and cpu usage.
        ## time.sleep(0.025)
        event.RequestMore()

    def GetImage(self):
        ## returns a PIL image for processing in a different application
        return self.video.GetImage()

class DummyCam:
    def __init__(self):
        testImagePath = os.path.dirname(__file__) + "/../test/test.jpg"
        self.testImage = Image.open(testImagePath)

    def getImage(self):
        return self.testImage

""" Test code
#####################################################
"""

class TrayApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers() # called so a PNG can be saved
        frame = VideoFrame(None)
        frame.Show(true)

        ## initialize a drawing
        ## It doesn't seem like this should be here, but the Frame does
        ## not get sized until Show() is called, so it doesn't work if
        ## it is put in the __init__ method.
        #frame.Run()

        self.SetTopWindow(frame)

        return true




if __name__ == "__main__":
    app = TrayApp(0)
    app.MainLoop()
