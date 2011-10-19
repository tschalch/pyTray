# This module is used for screen calculation
# Author: Thomas Schalch
# Date: 01/12/2007

import random
from util.ordereddict import oDict

class ScreenGenerator:

    def __init__(self, data):
        self.data = data
        self.InitFactors()
        
    def CreateRandomScreen(self):
        noWells = self.data.noWells
        for type in self.factors:
            wells = []
            for reagent in self.factors[type]:
                frequency = reagent.GetProperty("frequency")
                (min, max) = (reagent.GetProperty("minConc"), reagent.GetProperty("maxConc"))
                noSamples = int(frequency * noWells)
                increment = (max - min) / noSamples
                concentrations = [min + i * increment for i in range(noSamples)]
                wells.extend([(reagent, concentrations[i]) for i in range(noSamples)])
            if len(wells) < noWells:
                noSamples = noWells - len(wells)
                wells.extend([(None,None) for i in range(noSamples)])
            random.shuffle(wells)
            for i in range(noWells):
                components = self.data.dbBackend.GetChildren(self.data.GetScreenSolution(i), "Component")
                component = None
                for c in components:
                    if self.data.GetReagent(c.GetProperty("SolID")).GetProperty("type") == type:
                        component = c
                if not wells[i][0]:
                    if component:
                        component.Delete()
                    continue
                id = wells[i][0].GetAttribute("id")
                if not component:
                    component = self.data.AddNewComponent(self.data.GetScreenSolution, [i])
                component.SetProperty("SolID", id)
                component.SetProperty("Concentration", "%4.2f"%wells[i][1])
                                
    def InitFactors(self):
        self.factors = {}
        reagents = self.data.GetReagents()
        for reagent in reagents:
            id = int(reagent.GetAttribute("id"))
            type = reagent.GetProperty("type")
            minConc = reagent.GetProperty("minConc")
            maxConc = reagent.GetProperty("maxConc")
            if minConc == 0 and maxConc == 0:
                continue
            frequency = reagent.GetProperty("frequency")
            if not frequency:
                continue
            if not self.factors.has_key(type):
                self.factors[type] = []
            self.factors[type].append(reagent)
            #print "Adding reagent:\n%s\n\n" % (reagent.PrettyPrint())
