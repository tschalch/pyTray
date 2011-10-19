#!/usr/bin/env python2.4

"""
tray_data provides the data for the tray GUI.
It handles the XML data and provides the neccessary interfaces.

"""

import tray_data
import logging
from util.trayErrors import PropertyNotFoundError


log = logging.getLogger("xml_jtray")
log.setLevel(logging.WARN)


class JTrayData(tray_data.TrayData):

    """
    Main class for the handling of xml data from JTray files.
    """
    
    def __init__(self, dbBackend, new, UserData, controller=None):
        tray_data.TrayData.__init__(self, dbBackend, new, UserData)

    def BuildTray(self):
        tray_data.TrayData.InitScreen(self)
        self.screen.SetAttribute("Version","1.0")
#        self.noRows = int(self.doc.getElementsByTagName('NoRows')[0].firstChild.data)
#        self.noCols = int(self.doc.getElementsByTagName('NoCols')[0].firstChild.data)
#        self.noWells = self.noRows * self.noCols
#        noDrops = self.doc.createElement("NoDrops")
#        noDrops.appendChild(self.doc.createTextNode("1"))
#        self.screen.AddChild(noDrops)
#        self.noDrops = 1
        self.InitReagents()
        self.InitScreenSolution()
        self.InitDrops()
        self.InitScoring()
        self.InitRemarks()
        self.SetChanged(True)

    def InitRemarks(self):
        try:
        	remarks = self.screen.GetProperty("ExperimentRemarks")
	        newRemarks = "Temperature: " + str(self.screen.GetProperty("Temperature"))\
                    + "\nSetup Date: " + unicode(self.screen.GetProperty("ExpDate"))\
                    + "\nRemarks: " + remarks
        	self.screen.SetProperty("ExperimentRemarks",newRemarks)
       	except PropertyNotFoundError:
 	       self.screen.SetProperty('ExperimentRemarks', \
                                "Temperature:\nSetup Date:\nRemarks:")
 

    def InitScreenSolution(self):
    
        wellList = self.dbBackend.GetItems('Well')
        
        for well in wellList:
            try:
                dilutionFactor = well.GetProperty('ReservoirDilution')
            except PropertyNotFoundError:
                dilutionFactor = 1.0
            ## Create a new element for the Screen Solution
            screenSolution = self.dbBackend.GetNewItem("ScreenSolution", self.screen)
            ## Add a position element
            row = int(well.GetProperty("Row")) - 1
            col = int(well.GetProperty("Col")) - 1
            position = row * self.noCols +  col
            screenSolution.SetProperty("Position", position)
            self.screenSolutions[position] = screenSolution

            ## Create a new element for the Reservoir
            reservoir = self.dbBackend.GetNewItem("Reservoir", self.screen)
            reservoir.SetProperty("Position", position)
            self.reservoirs[position] = reservoir
            
            # add solution components to reservoir 
            compList = self.dbBackend.GetChildren(well, 'Ingredient')
            for i in compList:
            	i.element.tag = "Component"
                screenSolution.AddChild(i.GetCopy())
                reservoir.AddChild(i.GetCopy())

            self.screen.AddChild(screenSolution)     
            self.screen.AddChild(reservoir)     
            
            # extract the Observations
            obsList = self.dbBackend.GetChildren(well,'Observation')
            for o in obsList:
                ## Set well position and drop number
                observation = o.GetCopy()
                observation.SetProperty("Position", position)
                dropNr = 0
                observation.SetProperty("DropNr", dropNr)
                date = o.GetProperty('ObservationDate')
                ## add the observation date container, if not present
                if date and self.observationDates.count(date) < 1:
                    otp = self.dbBackend.GetNewItem("ObservationTimePoint", self.screen)
                    otp.SetProperty("TimePoint", date)
                    self.observations[date] = otp
                    self.observations[date].observations = {}
                    self.screen.AddChild(otp)
                    self.observationDates.append(date)
                obsoleteFields = ['ObservationDate','ScoreValue2','ScoreValue3']
                for f in obsoleteFields:
                    observation.RemoveChild(f)
                images = self.dbBackend.GetChildren(observation, "ObservationImage")
                for img in images:
                    try:
                        newName = date + "_" + str(row) +  "_" + str(col+1) +  "_" + img.GetText() + ".jpg"
                        img.SetText(newName)
                    except TypeError:
                        observation.RemoveChild("ObservationImage")
                self.observations[date].AddChild(observation)
                self.observations[date].observations[(position,dropNr)] = observation
                o.Delete()
            well.Delete()


    def InitDrops(self):
        """
        Builds a drop object for each well from the sample entry in JTray
        """

        # get sample and drop info out of jtray
        try:
            drop = self.dbBackend.GetItems('Drop')[0]
            sample = self.dbBackend.GetItems('Sample')[0]
        except IndexError:
            # this happens when no drop is available => only screen files
            return
        # create new drop component
	sampleComponent = self.dbBackend.GetNewItem("DropComponent",self.screen)
        # transfer sample information
        sampleComponent.SetProperty('Description', sample.GetProperty('Description'))
        sampleComponent.SetProperty('Concentration', sample.GetProperty('SampleConcentration'))
        sampleComponent.SetProperty('Volume', drop.GetProperty('SampleVol'))
        sampleComponent.SetProperty('Buffer', sample.GetProperty('SampleBuffer'))
        sampleComponent.SetProperty('Remarks', "")
        ## transfer drop solution information
        solComponent = self.dbBackend.GetNewItem("DropComponent",self.screen)
        solComponent.SetProperty('Description', "Screen Solution")
        solComponent.SetProperty('Concentration', "0")
        solComponent.SetProperty('Buffer', "")
        solComponent.SetProperty('Volume', drop.GetProperty("ResVol"))
        solComponent.SetProperty('Remarks', "")
        drop.Delete()
        sample.Delete()
        
        for i in range(self.noWells):
            drop = self.dbBackend.GetNewItem("Drop",self.screen)
            self.screen.AddChild(drop)
            drop.SetProperty("Position", i)
            drop.SetProperty("DropNr", 0)
            sampleComponent.parent = drop
            solComponent.parent = drop
            drop.AddChild(sampleComponent.GetCopy())
            drop.AddChild(solComponent.GetCopy())
            self.drops[(drop.GetProperty("Position"), drop.GetProperty("DropNr"))] = drop



if __name__ == "__main__":
    from elmtree_backend import OpenFile
    data = OpenFile("D:/Screens/4x_3x_Constructs/Experiments/030606_12x167_H1_4C.exp",
          "U:/Personal/Programming/pyTray/src/files/Dtd/definition.xml")
    data.dbBackend.Print()
    #xml.dom.ext.PrettyPrint(data.doc)
    #data.printDoc()


