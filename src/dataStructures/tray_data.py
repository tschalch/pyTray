#!/usr/bin/env python2.4

"""
tray_data provides the data for the tray GUI.
It handles the XML data and provides the neccessary interfaces.

"""

import logging, os, os.path
from util.ordereddict import oDict
from util.trayErrors import NoObservationError, NoUndoError, DoubleEmptyRecordError, PropertyNotFoundError
import dataStructures
import PIL.Image

log = logging.getLogger("tray_data")
log.setLevel(logging.WARN)

# debugging with winpdb:
#import rpdb2
#rpdb2.start_embedded_debugger("test")

class TrayData:
    
    IMAGE_SIZE = (240,194)

    def __init__(self, dbBackend, newScreen=None, userData=None, controller=None):
        # setup variables
        self.reagents = []
        self.screenSolutions = {}
        self.observations = {}
        self.observationDates = []
        self.observationDate = 0
        self.drops = {}         ## dictionary keys are (wellNr, dropNr) tuple
        self.reservoirs = {}
        self.scores = oDict ()
        self.eventListeners = {}
        self.changed = False
        self.undoQueue = []
        self.backups = []    ## list to contain backup docs for undo actions
        dataStructures.changingItems.append(self)
        
        self.noRows = 0
        self.noCols = 0

        self.userData = userData
        self.dbBackend = dbBackend
        self.controller = controller

        if newScreen:
            self.InitNewScreen(newScreen)
        else:
            self.BuildTray()


    def AddEventListener(self, updateGroup, listener):
        if not self.eventListeners.has_key(updateGroup):
            self.eventListeners[updateGroup] = []
        self.eventListeners[updateGroup].append(listener)


    def AddImage(self, image):
	assert os.path.isfile(image)
        drops = self.GetActiveDrops()
        if len(drops) == 1 and self.observationDate:
            position = drops[0]
            obs = self.GetObservation(self.observationDate,position)
            if type(image) is unicode or type(image) is str:
                image = PIL.Image.open(image)
            nr = 0
            imageName = "img_" + self.observationDate + "_" + str(position[0]) + "_"\
                         + str(position[1]) + "_" + str(nr) + ".jpg"
            while not self.dbBackend.AddImage(image, imageName):
                nr += 1
                imageName = "img_" + self.observationDate + "_" + str(position[0])\
                             + "_" + str(position[1]) + "_" + str(nr) + ".jpg"
            newImage = self.dbBackend.GetNewItem("ObservationImage", obs)
            newImage.SetText(imageName)
            obs.SaveState(self.undoQueue)
            obs.AddChild(newImage)
            self.SetChanged(True)
        self.SaveBackup()

    def AddNewComponent(self, getContainerFunction, positions = None):
        if positions:
            wells = positions
        else:
            wells = self.GetActiveWells()
        newComponent = None
        for well in wells:
            try:
                container = getContainerFunction(well)
                if container:
                    # check for empty rows don't allow two empty rows in a well
                    components = self.dbBackend.GetChildren(container, "Component")
                    for component in components:
                        firstField = component.GetProperty("SolID")
                        if firstField == "":
                            raise DoubleEmptyRecordError("This well already contains a new component")
                    container.SaveState(self.undoQueue)
                    newComponent = self.dbBackend.GetNewItem('Component', container)
                    container.AddChild(newComponent)
            except DoubleEmptyRecordError:
                # skip this component and goto next
                pass
        self.SaveBackup()
        return newComponent

    def AddNewDropComponent(self):
        drops = self.GetActiveDrops()
        for drop in drops:
            try:
                drop = self.GetDrop(drop)
                if drop:
                    # check for empty rows don't allow two empty rows in a well
                    components = self.dbBackend.GetChildren(drop, "DropComponent")
                    for component in components:
                        firstField = component.GetProperty("Description")
                        if firstField == "":
                            raise DoubleEmptyRecordError("This well contains already an new component")
                    drop.SaveState(self.undoQueue)
                    newComponent = self.dbBackend.GetNewItem('DropComponent', drop)
                    drop.AddChild(newComponent)
            except DoubleEmptyRecordError:
                # skip this component and goto next
                pass
        self.SaveBackup()

    def AddNewReagent(self):
        self.screen.SaveState(self.undoQueue)
        newReagent = self.dbBackend.GetNewItem('Stock_Reagent', self.screen)
        id = self.GetNewReagentID()
        newReagent.SetAttribute("id",str(id))
        self.screen.AddChild(newReagent)
        self.reagents.append(newReagent)
        self.SaveBackup()
        return newReagent

    def AddNewReservoir(self, position):
        #add a reservoir container to each well
        reservoir = self.dbBackend.GetNewItem("Reservoir", self.screen)
        reservoir.SetProperty("Position", position)
        self.reservoirs[position] = reservoir
        self.screen.AddChild(reservoir)

    def AddNewScore(self, id):
        self.screen.SaveState(self.undoQueue)
        newScore = self.dbBackend.GetNewItem('Score', self.screen)
        self.screen.AddChild(newScore)
        newScore.SetProperty("ScoreNr", id)
        newScore.SetProperty("ScoreColor","#000000")
        self.scores[id] = newScore
        self.SaveBackup()

    def AddNewScreenSolution(self, position, solutionNr=None):
        # add a solution container to each well
        # print "SolNr:", solutionNr
        screenSolution = self.dbBackend.GetNewItem('ScreenSolution', self.screen)
        screenSolution.SetProperty("Position", position)
        if solutionNr:
            screenSolution.SetProperty("SolutionNr", solutionNr)
        else:
            screenSolution.SetProperty("SolutionNr", position)
        self.screenSolutions[position] = screenSolution
        self.screen.AddChild(screenSolution)

    def AddNewObservation(self, description):
        self.screen.SaveState(self.undoQueue)
        observationTimePoint = self.dbBackend.GetNewItem('ObservationTimePoint', self.screen)
        observationTimePoint.SetProperty('TimePoint', description)
        self.screen.AddChild(observationTimePoint)
        self.observationDates.append(description)
        self.observations[description] = observationTimePoint
        self.observations[description].observations = {}
        
        for i in range(self.noWells):
            log.debug("NoDrops: %s", self.noDrops)
            for j in range(self.noDrops):
                observation = self.dbBackend.GetNewItem('Observation', observationTimePoint)
                observationTimePoint.AddChild(observation)
                observation.SetProperty("Position", str(i))
                observation.SetProperty("DropNr", str(j))
                self.observations[description].observations[(i,j)] = observation
        self.SetChanged(True)
        self.SaveBackup()

    def AddReagent(self, reagent):
        self.screen.AddChild(reagent)
        self.reagents.append(reagent)


    def BuildTray(self):
        self.InitScreen()
        self.InitReagents()
        self.InitScreenSolutions()
        self.InitReservoirs()
        self.InitObservations()
        self.InitDrops()
        self.InitScoring()
        pass

    def DeleteImage(self, image):
        image.SaveState(self.undoQueue, None)
        parent = self.dbBackend.GetParent(image)
        image.Delete(parent)
        self.SetChanged(True)
        self.SaveBackup()

    def DeleteObservation(self, obs):
        observation = self.observations.pop(obs)
        self.observationDates.remove(observation.GetProperty('TimePoint'))
        observation.Delete()

    def DeleteScreenSolutions(self):
        wells = self.GetActiveWells()
        for well in wells:
            sol = self.screenSolutions[well]
            #print sol.PrettyPrint()
            sol.SaveState(self.undoQueue,None)
            sol.Delete(self.screen.element)
            del self.screenSolutions[well]
            sol = self.GetScreenSolution(well)
            #print sol.PrettyPrint()
        self.SetChanged(True)
        self.SaveBackup()
        self.UpdateEventListeners(["screen"], None)

    def Close(self):
        self.dbBackend.Close()

    def GetActiveDrops(self):
        activeDrops = []
        for position,drop in self.drops.iteritems():
            if drop.selected:
                activeDrops.append(position)
        return activeDrops

    def GetActiveReservoirs(self):
        activeReservoirs = []
        for p,r in self.reservoirs.iteritems():
            if r.selected:
                activeReservoirs.append(p)
        return activeReservoirs

    def GetActiveReservoir(self):
        well = self.GetActiveWells()
        if len(well) == 1:
            return self.reservoirs[well[0]]
        return None

    def GetActiveWells(self):
        wells = []
        for p,r in self.reservoirs.iteritems():
            if r.selected:
                wells.append(p)
        for p,d in self.drops.iteritems():
            if d.selected:
                if not wells.count(p[0]):
                    wells.append(p[0])
        return wells

    def GetAlphabetPosition(self, position):
        alphabet = {1:"A", 2:"B", 3:"C", 4:"D", 5:"E", 6:"F", 7:"G",\
                    8:"H", 9:"I", 10:"J", 11:"K", 12:"L", 13:"M", 14:"N",\
                    15:"O", 16:"P", 17:"Q", 18:"R", 19:"S", 20:"T", 21:"U",\
                    22:"V", 23:"W", 24:"X", 25:"Y", 26:"Z"}
        row = alphabet[int(position / self.noCols) + 1]
        col = position % self.noCols + 1
        return (row,col)

    def GetDrop(self, position):
        return self.drops[position]

    def GetExperimentParams(self):
        return self.screen.GetProperty("ExperimentRemarks")

    def GetFilename(self):
        filename = self.dbBackend.GetFilename()
        if filename:
            return os.path.split(filename)[1]
        else:
            return "Untitled"

    def GetImages(self,date=None,position=None):
        if not date and not position:
            return self.dbBackend.GetItems("ObservationTimePoint/Observation/ObservationImage")            
        well, drop = position
        images = []
        if date:
            images = self.dbBackend.GetChildren(\
                self.observations[date].observations[(well,drop)],"ObservationImage")
        elif self.observationDate:
            images = self.dbBackend.GetChildren(\
                self.observations[self.observationDate].observations[(well,drop)],\
                "ObservationImage")
        return images

    def GetNewReagentID(self):
        solIDCounter = self.screen.GetProperty("SolIDCounter")
        solIDCounter += 1
        self.screen.SetProperty("SolIDCounter",solIDCounter)
        return solIDCounter

    def GetNrDrops(self):
        position = 0
        counter = 0
        while 1:
            if  self.drops.has_key((position, counter)):
                counter += 1
            else:
                return counter
        return counter

    def GetObservation(self, date, position):
        well, drop = position
        if date:
            return self.observations[date].observations[position]
        elif self.observationDate:
            return self.observations[self.observationDate].observations[position]
        else:
            return 0

    def GetObservationDates(self):
        return self.observationDates

    def GetReagent(self, r):
        index = None
        if type(r) == type(int(1)):
            reagNrs = [int(reag.GetAttribute("id")) for reag in self.reagents]
            index = reagNrs.index(r)
        elif type(r) == type("string"):
            reagNames = [reag.GetProperty("name") for reag in self.reagents]
            #print "reagent: ", r
            index = reagNames.index(r)
        if index != None:
            try:
                return self.reagents[index]
            except KeyError:
                return None
        else:
            return None

    def GetReagents(self):
        return self.reagents

    def GetReservoir(self, position):
        try:
            return self.reservoirs[position]
        except KeyError:
            self.AddNewReservoir(position)
            return self.reservoirs[position]

    def GetReservoirs(self):
        return self.reservoirs

    def GetScoreColor(self, scoreNr):
        if scoreNr > -10:
            score = self.scores[scoreNr]
            log.debug("Score %s", score.GetProperty("ScoreText"))
            return score.GetProperty("ScoreColor")
        else:
            raise KeyError

    def GetScores(self):
        self.InitScoring()
        return self.scores

    def GetScreen(self):
        return self.screen

    def GetScreenName(self):
        return self.screen.GetAttribute('name')

    def GetScreenSolution(self, position):
        try:
            return self.screenSolutions[position]
        except KeyError:
            if position < self.noWells and position >= 0:
                self.AddNewScreenSolution(position)
                return self.screenSolutions[position]

    def GetScreenSolutions(self):
        return self.screenSolutions

    def GetSummary(self):
        observations = len(self.observations)
        #reagents = len(self.dbBackend.GetItems('Stock_Reagent'))
        reagents = len(self.reagents)
        scores = len(self.scores)
        ss = len(self.screenSolutions)
        res = len(self.reservoirs)
        drops = len(self.drops)
        imgs = len(self.dbBackend.GetItems("ObservationTimePoint/Observation/ObservationImage"))
        sum = "Summary of pyTray file %s:" % (self.GetFilename())
        sum += "\n*****************************************************************************\n"
        sum += "%s\n" % (self.GetScreenName())
        sum += "Rows:\t\t%4i\tColumns:\t\t%4i\tWells:\t%4i\n" % (self.noRows,self.noCols,self.noWells)
        sum += "Reagents:\t%4i\tScreen Solutions:\t%4i\tDrops:\t%4i\n" % \
                (reagents,ss,drops)
        sum += "Observations:\t%4i\tScores:\t%4i\tReservoirs:\t%4i\tImages:\t%4i\n" % (observations,scores,res,imgs)
        if scores == 0:
            sum += "!!!!!!!!!!!!! Scores missing !!!!!!!!!!!!!!!!!!!1"
        sum += "*****************************************************************************\n"
        return sum

    def HasChanged(self):
        for i in dataStructures.changingItems:
            if i.changed:
                return True

    def ImportReagents(self, source):
        """
        Imports data from another tray file.
        source parameter is an XMLTrayData object
        """
        # remove all reagents
        for reagent in self.reagents:
            reagent.Delete()
        # import reagents
        for reagent in source.GetReagents():
            copyReag = reagent.GetCopy()
            self.screen.AddChild(copyReag)
            self.reagents.append(copyReag)
        # set reagent ID counter to the value in the source file
        self.screen.SetProperty("SolIDCounter", source.screen.GetProperty("SolIDCounter"))
    
    def ImportScreenSolutions(self, source):
        """
        Imports data from another tray file.
        source parameter is an XMLTrayData object
        """
        # remove all screen solutions
        self.ResetScreenSolutions()
        # import screen solutions
        for key,screenSol in source.GetScreenSolutions().items():
            copyScreenSol = screenSol.GetCopy()
            self.screen.AddChild(copyScreenSol)
            self.screenSolutions[key] = copyScreenSol

    def ImportReservoirs(self, source):
        """
        Imports data from another tray file.
        source parameter is an XMLTrayData object
        """
        # remove all reservoir solutions
        self.ResetReservoirSolutions()
        # import reservoir solutions
        for key,reservoir in source.GetReservoirs().items():
            copyReservoir = reservoir.GetCopy()
            self.screen.AddChild(copyReservoir)
            self.reservoirs[key] = copyReservoir

    def ImportScores(self, source):
        """
        Imports data from another tray file.
        source parameter is an XMLTrayData object
        """
        # remove all reservoir solutions
        for score in self.scores.values():
            score.Delete()
        self.scores.clear()
        # import reservoir solutions
        for key,score in source.GetScores().items():
            copyScore = score.GetCopy()
            self.screen.AddChild(copyScore)
            self.scores[key] = copyScore

    def ImportStockSolutions(self, source):
        self.screen.SaveState(self.undoQueue)
        self.ResetReservoirSolutions()
        self.ResetScreenSolutions()
        self.ResetReagents()
        newReagents = source.GetReagents()
        for nR in newReagents:
            newReagent = nR.GetCopy()
            self.AddReagent(newReagent)
        self.screen.SetProperty("SolIDCounter", source.screen.GetProperty("SolIDCounter"))
        self.SaveBackup()

    def InitNewScreen(self, newScreen):
        """
        newScreen parameter: Dictionary of values necessary for initialization of screen
        {ScreenName, NoRows, NoCols, NoDrops, WellVolume, VolumeUnit}
        """
        self.screen = self.dbBackend.GetRoot()
        self.screen.SetAttribute("name", newScreen["ScreenName"])
        self.screen.SetProperty('NoRows', newScreen["NoRows"])
        self.screen.SetProperty('NoCols', newScreen["NoCols"])
        self.screen.SetProperty('NoDrops', newScreen["NoDrops"])
        self.screen.SetProperty('SolIDCounter', 0)
        self.screen.SetProperty('ExperimentRemarks', \
                                "Temperature:\nSetup Date:\nRemarks:")
        self.InitScreen()

        for i in range(self.noWells):
            # add a solution container to each well
            self.AddNewScreenSolution(i)
            #add a reservoir container to each well
            self.AddNewReservoir(i)
            #add the drop containers
            for d in range(self.noDrops):
                drop = self.dbBackend.GetNewItem('Drop', self.screen)
                drop.SetProperty("Position", i)
                drop.SetProperty("DropNr", d)
                self.drops[(i,d)] = drop
                self.screen.AddChild(drop)

        self.ImportScores(self.userData)
        
        
    def InitScreen(self):

        self.screen = self.dbBackend.GetRoot()
        self.noRows = self.screen.GetProperty('NoRows')
        self.noCols = self.screen.GetProperty('NoCols')
        self.noWells = self.noRows * self.noCols
        try:
        	if self.screen.GetProperty('NoDrops'):
        	    self.noDrops = self.screen.GetProperty('NoDrops')
        	else:
        	    raise PropertyNotFoundError("Error")
        except PropertyNotFoundError:
            self.screen.SetProperty('NoDrops', 1)
            self.noDrops = self.screen.GetProperty('NoDrops')


    def InitReagents(self):
        reagList = self.dbBackend.GetItems('Stock_Reagent')
        for reagent in reagList:
            self.reagents.append(reagent)


    def InitScreenSolutions(self):
        screenSolList = self.dbBackend.GetItems('ScreenSolution')
        for solution in screenSolList:
            self.screenSolutions[solution.GetProperty("Position")] = solution


    def InitReservoirs(self):
        reservoirList = self.dbBackend.GetItems('Reservoir')
        for reservoir in reservoirList:
            self.reservoirs[reservoir.GetProperty("Position")] = reservoir


    def InitReservoirsFromScreen(self):
        self.screen.SaveState(self.undoQueue)
        for res in self.reservoirs.values():
            res.Delete()
        self.reservoirs.clear()
        for position,sol in self.screenSolutions.items():
            reservoir = self.dbBackend.GetNewItem("Reservoir", self.screen)
            reservoir.SetProperty("Position", position)
            self.reservoirs[position] = reservoir
            self.screen.AddChild(reservoir)
            for component in self.dbBackend.GetChildren(sol, "Component"):
                reservoir.AddChild(component.GetCopy())
        self.SaveBackup()
    
    def InitDrops(self):
        dropList = self.dbBackend.GetItems('Drop')
        for drop in dropList:
            self.drops[(drop.GetProperty("Position"), drop.GetProperty("DropNr"))] = drop


    def InitObservations(self):
        obsTimePList = self.dbBackend.GetItems('ObservationTimePoint')
        for observationTimePoint in obsTimePList:
            otpDate = observationTimePoint.GetProperty('TimePoint')
            self.observationDates.append(otpDate)
            self.observations[otpDate] = observationTimePoint
            self.observations[otpDate].observations = {}
            obs = self.dbBackend.GetChildren(observationTimePoint, 'Observation')
            for o in obs:
                #images = o.GetChildren("ObservationImage")
                #if len(images) > 0:
                    # delete empt image elements
                #    if not images[0].GetText():
                #        images[0].Delete()
                drop = (o.GetProperty("Position"),o.GetProperty("DropNr"))
                self.observations[otpDate].observations[drop] = o
        

    def InitScoring(self):
        self.scores = oDict()
        try:
            scorelist = self.dbBackend.GetItems('ScoreList')[0]
        except IndexError:
            scorelist = None
        if scorelist:
            scores = self.dbBackend.GetChildren(scorelist,"Score")
            for score in scores:
                self.screen.AddChild(score)
                self.scores[score.GetProperty('ScoreNr')] = score
            scorelist.Delete()
        else:
            scores = self.dbBackend.GetItems('Score')
            for score in scores:
                self.scores[score.GetProperty('ScoreNr')] = score

    def MultiplyScreenSolutions(self, factor):
        actWells = self.GetActiveWells()
        for position in actWells:
            solution = self.screenSolutions[position]
            solution.SaveState(self.undoQueue)
            components = self.dbBackend.GetChildren(solution, "Component")
            for component in components:
                conc = component.GetProperty("Concentration")
                conc = conc * factor
                component.SetProperty("Concentration", conc)
        self.SaveBackup()
    
    def MultiplyReservoirSolutions(self, factor):
        actWells = self.GetActiveWells()
        for position in actWells:
            solution = self.reservoirs[position]
            solution.SaveState(self.undoQueue)
            components = self.dbBackend.GetChildren(solution, "Component")
            for component in components:
                conc = component.GetProperty("Concentration")
                conc = conc * factor
                component.SetProperty("Concentration", conc)
        self.SaveBackup()

    def Open(self, filename):
        pass

    def OpenImage(self, image):
        self.dbBackend.OpenImage(image.GetText())

    def RenameObservation(self, obs, newName):
        observation = self.observations.pop(obs)
        observation.SetProperty("TimePoint", newName)
        self.observations[newName] = observation

    def Reset(self):
        self.reagents = []
        self.screenSolutions = {}
        self.observations = {}
        self.observationDates = []
        self.drops = {}         ## dictionary keys are (wellNr, dropNr) tuple
        self.reservoirs = {}
        self.scores = oDict ()

    def ResetChanged(self):
        for i in dataStructures.changingItems:
            i.SetChanged(False)

    def ResetReagents(self):
        for reagent in self.reagents:
            reagent.Delete()
        del self.reagents[:]

    def ResetReservoirSolutions(self):
        for reservoir in self.reservoirs.values():
            components = reservoir.GetChildren("Component")
            for c in components:
                c.Delete()

    def ResetScreenSolutions(self):
        for screenSol in self.screenSolutions.values():
            components = screenSol.GetChildren("Component")
            for c in components:
                c.Delete()
            

    def RemoveUnusedReagents(self):
        usedReagents = []
        for screenSol in self.GetScreenSolutions().values():
            for component in screenSol.GetChildren('Component'):
                id = int(component.GetProperty('SolID'))
                try:
                    usedReagents.index(self.GetReagent(id))
                except ValueError:
                    usedReagents.append(self.GetReagent(id))
        self.ResetReagents()
        for reagents in usedReagents:
            self.AddReagent(reagents)
        

    def Save(self, filename=None):
        self.dbBackend.Save(filename)
        self.ResetChanged()

    def SaveSimplexData(self, path):
        try:
            lastDate = self.GetObservationDates()[-1]
        except IndexError:
            print "no Observations to export"
            return
        for j in range(self.noDrops):
            exportData = []
            for i in range(len(self.reservoirs)):
                obs = self.GetObservation(lastDate,(i,j))
                screenSolution = self.GetScreenSolution(i)
                record = ["%s,%s,%s\n" % (self.GetScreenName(), screenSolution.GetProperty("SolutionNr"), obs.GetProperty("ScoreValue"))]
                exportData.append(record)
            # write to file
            try:
                spath = os.path.splitext(path)
                fout = open("%s_drop%i%s" % (spath[0],j,spath[1]),"w")
            except Exception,e:
                print "Writing file failed"
                raise
            fout.write("#Screen Name, SolutionNr, Score\n")
            for record in exportData:
                fout.write(record[0])
            fout.close()
    
    def SaveAnalysisData(self, path):
        exportData = []
        #print self.GetObservationDates();
        for date in self.GetObservationDates():
            for i in range(len(self.reservoirs)):
                for j in range(self.noDrops):
                    obs = self.GetObservation(date,(i,j))
                    reservoir = self.GetReservoir(i)
		    drop = self.GetDrop((i,j))
                    reagents = self.dbBackend.GetChildren(reservoir, "Component")
                    for component in reagents:
                        reagent = self.GetReagent(component.GetProperty("SolID"))
                        record = []
                        record.extend([date, (i,j), reagent, component.GetProperty("Concentration"), obs.GetProperty("ScoreValue")])
                        exportData.append(record)
        # write to file
        try:
            fout = open(path,"w")
        except Exception,e:
            print "Writing file failed"
            raise
        fout.write("# date; well; drop; reagent name; concentration; unit; type; pH; ionic strength; hydrophobicity; score\n")
        for record in exportData:
            reagent = record[2]
            reagentString = '%s;%6.2f;%s;%s;%6.2f;%6.2f;%6.2f' % (reagent.GetProperty("name"),
                                          record[3],
                                          reagent.GetProperty("unit"),
                                          reagent.GetProperty("type"),
                                          reagent.GetProperty("ph"),
                                          reagent.GetProperty("ionicstrength"),
                                          reagent.GetProperty("hydrophobicity"))
            print record
            if record[4] == None:
                strRecord = "%s;%i;%i;%s;NA\n" % (record[0], record[1][0], record[1][1], reagentString)
            else:
                strRecord = "%s;%i;%i;%s;%6.2f\n" % (record[0], record[1][0], record[1][1], reagentString, float(record[4]))
            fout.write(strRecord)
        fout.close()
            

    def SaveBackup(self):
        #return
        """
        Copy current state into backup list
        """
        self.backups.append(self.undoQueue[:])
        self.undoQueue = []
        if len(self.backups) > 30: self.backups.pop(0)

    def SetChanged(self, state):
        self.changed = state
        #if state:
            #print "Tray change registered"

    def SetExperimentParams(self, text):
        self.screen.SetProperty("ExperimentRemarks", unicode(text))

    def SetObservationDate(self, date):
        self.observationDate = date

    def SetNewObservation(self, description):
        pass

    def SetObservationRemarks(self, remarks):
        drops = self.GetActiveDrops()
        for drop in drops:
            obs = self.GetObservation(0, drop)
            #obs.SaveState(self.undoQueue)
            obs.SetProperty("ObservationRemarks", remarks)
        #self.SaveBackup()

    def SetScore(self, score):
        if not self.observationDates:
            raise NoObservationError("Trying to set score without observation")
        if self.scores.has_key(score):
            drops = self.GetActiveDrops()
            for drop in drops:
                obs = self.GetObservation(0, drop)
                obs.SaveState(self.undoQueue)
                obs.SetProperty("ScoreValue", score)
            self.SaveBackup()

    def SetScreenName(self, name):
        self.screen.SaveState(self.undoQueue)
        self.screen.SetAttribute('name', name)
        self.SaveBackup()

    def SortReagents(self, field):
        sortList = []
        for reagent in self.reagents:
            sortList.append(reagent)
        sortList.sort(key=lambda x: x.GetProperty(field))
        self.ResetReagents()
        for reagent in sortList:
            self.AddReagent(reagent)


    def Undo(self):
        #return
        if len(self.backups):
            for undoAction in self.backups.pop():
                parent = undoAction[0]
                oldItem = undoAction[1]
                newItem = undoAction[2]
                #print "parent: %s oldE: %s newE: %s" % (parent, oldElement, newElement)
                if oldItem:
                    parent.ReplaceChild(newItem, oldItem)
                else:
                    parent.AddChild(newItem)
            self.Reset()
            self.BuildTray()
            self.UpdateEventListeners(None, None)
            self.UpdateEventListeners(["tray"], None)
        else:
            raise tray_data.NoUndoError("No more Undo actions.")

    def UpdateEventListeners(self, groups, sender):
        #print "updating group: %s" % groups
        #print sender
        if groups:
            for g in groups:
                #print "groups: %s, group: %s " % (groups, g)
                if g == "tray" and self.eventListeners.has_key(g):
                    for l in self.eventListeners[g]:
                        l.OnSize(None)
                if self.eventListeners.has_key(g):
                    for l in self.eventListeners[g]:
                        #print "updating %s" % l
                        l.OnDataChange()
                if sender:
                    sender.SetFocus()
        else:
            for group in self.eventListeners.values():
                for l in group:
                    l.OnDataChange()
                if sender:
                    sender.SetFocus()
        #print "done"
                

if __name__ == "__main__":
    data = TrayData()
    #data.printDoc()


