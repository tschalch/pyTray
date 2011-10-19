#! /usr/bin/env python

# Class for storing user-specific data

import user
import os, os.path
from util.ordereddict import oDict
import elmtree_backend

if os.name == 'nt':
    apdir = os.environ["APPDATA"] + "\\PyTray"
    if not os.path.exists(apdir):
        os.mkdir(os.environ["APPDATA"] + "\\PyTray")
    oldfile = user.home + "/.pyTray"
    configFile = apdir + "\\user.pyTray"
    if os.path.exists(oldfile) and not os.path.exists(configFile):
        os.rename(oldfile,configFile)
else:
    apdir = user.home
    configFile = apdir + "/.pyTray"
# clean up old temp files
for dirpath, dirnames, filenames in os.walk(apdir):
    for filename in filenames:
        if filename.find(".exp~") > 0:
            file = os.path.join(dirpath, filename)
            try:
                os.remove(file)
            except WindowsError:
                pass

class UserData:
    def __init__(self, controller):
        self.userTemplateFile = controller.userTemplateFile
        self.defDoc = controller.defFile
        self.scores = None
        if os.path.exists(configFile):
            self.backend = elmtree_backend.OpenFile(configFile, self.defDoc)
            self.prefs = self.backend.GetRoot()
        else:
            self.InitUserData()
        self.InitScoring()

    def GetPrefs(self):
        return self.prefs

    def GetTempDir(self):
        return os.path.abspath(apdir)

    def InitScoring(self):
        if self.scores:
            self.scores.clear()
        else:
            self.scores = {}
        scores = self.backend.GetChildren(self.prefs, 'ScoreList/Score')
        for score in scores:
            self.scores[score.GetProperty('ScoreNr')] = score

    def GetScores(self):
        return self.scores

    def GetValue(self, name):
        return self.prefs.GetProperty(name)

    def InitUserData(self):
        self.backend = elmtree_backend.OpenFile(self.userTemplateFile, self.defDoc)
        self.backend.Save(configFile, False)
        self.backend = elmtree_backend.OpenFile(configFile, self.defDoc)
        self.prefs = self.backend.GetRoot()
        self.SetValue("LastDir", user.home)

    def SetScoringSystem(self, scores):
        scorelist = self.backend.GetChildren(self.prefs, 'ScoreList')[0]
        oldScores = self.backend.GetChildren(scorelist, 'Score');
        for olScore in oldScores:
            olScore.Delete()
        for score in scores.values():
            scorelist.AddChild(score.GetCopy())
        kids = scorelist.GetChildren('Score');
        for kid in kids:
            print kid.GetProperty("ScoreText")
        self.Save()
        self.InitScoring()
        for score in self.scores.values():
            print score.GetProperty("ScoreText")

    def SetValue(self, name, value):
        self.prefs.SetProperty(name, value)
        self.backend.Save(None,False)

    def Save(self):
        self.backend.Save(None,False)
        self.prefs.SetChanged(False)

if __name__ == "__main__":
    ud = UserData("d:/thomas/Programming/python/pyTray/files/.pyTray")
    ud.SetValue("LastDir", "d:/thomas/Programming/python/pyTray/files/")
    ud.Save()
    
    #data.printDoc()

