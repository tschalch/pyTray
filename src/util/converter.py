# This program converts spreadsheed screen information to pyTray format
# Author: Thomas Schalch
# Date: 01/12/2007

import controller

def splitLine (line):
    return line.strip().split(';')
    

class Converter:

    def __init__(self, cvsdata, data):
        self.cvsdata = cvsdata
        self.components = []
        self.data = data
        self.fin = open(self.cvsdata,"r")
        self.lables = None
    
    def getRecordsFromCVS(self):
        records = []
        for line in self.fin:
            #print line
            if line[0] == "#": continue
            if line[0] == ",": continue
            if line[0] == ">":
                line = line.strip(">")
                self.lables = splitLine(line)
                continue
            if self.lables:
                tokens = splitLine(line)
                record = {}
                if tokens[0]:
                    for i in range(len(self.lables)):
                        #print lables[i],tokens[i]
                        try:
			    record[self.lables[i].strip(' "')] = tokens[i].strip(' "')
                        except IndexError:
                            print "label not found, entering empty string"
                            record[self.lables[i].strip()] = ""
                    records.append(record)
                else:
                    continue
            else:
                continue
        return records
    
    def convertSimplexScreen(self):
        self.data.ResetReservoirSolutions()
        self.data.ResetScreenSolutions()
        screenSols = self.getRecordsFromCVS()
        for cvsScreenSol in screenSols:
            position = int(cvsScreenSol['tube#'].split(' ')[1]) - 1
            del cvsScreenSol['tube#']
            screenSol = self.data.AddNewScreenSolution(position, position + 1)
            #print "values ", cvsScreenSol.values()
            for reag in cvsScreenSol.values():
                if reag == '':
                    continue
                reag = reag.split(' ')
                #print reag
                try:
                    ph = reag.index('pH')
                    reag[ph + 1] = "%2.1f" % (float(reag[ph+1]))
                except ValueError:
                    #print "No pH found"
                    pass
                reagName = ' '.join(reag[2:])
                reagent = self.data.GetReagent(reagName)
                if reagent == None:
                    reagent = self.data.AddNewReagent()
                    reagent.SetProperty('name', reagName)
                    reagent.SetProperty('unit', reag[1])                    
                component = self.data.AddNewComponent(self.data.GetScreenSolution, [position])
                component.SetProperty("SolID", reagent.GetAttribute("id"))
                component.SetProperty("Concentration", reag[0])
            
    def convertStocks(self):
        self.data.ResetReservoirSolutions()
        self.data.ResetScreenSolutions()
        self.data.ResetReagents()
        stocks = self.getRecordsFromCVS()
        #print stocks
        for cvsStock in stocks:
            print cvsStock
            reagent = self.data.AddNewReagent()
            try:
                name = cvsStock['name']
		reagent.SetProperty('name', name)
            except KeyError:
                print "Column 'name' not found in cvs file"
            try:
                ph = float(cvsStock['ph'])
                if ph >= 0: 
                    reagent.SetProperty('ph', ph)
                    name += " at pH %2.1f" % (ph)
            except KeyError:
                print "Column 'pH' not found in cvs file"
            try:
                reagent.SetProperty('concentration', cvsStock['concentration'])
            except KeyError:
                print "Column 'concentration' not found in cvs file"
            try:
                reagent.SetProperty('unit', cvsStock['unit'])
            except KeyError:
                print "Column 'unit' not found in cvs file"
            try:
                reagent.SetProperty('type', cvsStock['type'])
            except KeyError:
                print "Column 'type' not found in cvs file"
            try:
                reagent.SetProperty('reagRemarks', cvsStock['remarks'])
            except KeyError:
                print "Column 'remarks' not found in cvs file"
    
    def convert(self):
        self.data.ResetReservoirSolutions()
        self.data.ResetScreenSolutions()
        self.data.ResetReagents()
        noWells = self.data.noRows * self.data.noCols
        # read in cvs data
        reagents = {}
        lables = None
        for line in self.fin:
            #print line
            if line[0] == "#": continue
            if line[0] == ",": continue
            if line[0] == ">":
                line = line.strip(">")
                lables = splitLine(line)
		print lables
                for lable in lables:
                    l = lable.strip('[{}]" \n')
                    if not self.components.count(l) and (l!="Position" and l!="SolutionNr" and l!='pH') :
                        self.components.append(l)
                print self.components
                continue
            if lables:
                tokens = splitLine(line)
                record = {}
                if tokens[0]:
                    for i in range(len(lables)):
                        print lables[i],tokens[i]
                        try:
                            record[lables[i].strip(' "')] = tokens[i].strip(' "')
                        except IndexError:
                            record[lables[i].strip(' "')] = ""
                else:
                    continue
            else:
                continue
            print record
            # for every component extract name, concentration and units
            try:
                wellNr = int(record['Position'])
                position = wellNr -1
            except ValueError:
                print "Position not defined"
                continue
            try:
                solNr = int(record['SolutionNr'])
            except ValueError:
                print "SolutionNr not defined"
                continue
            if position >= noWells:
                break
            if not position in self.data.screenSolutions:
                self.data.AddNewScreenSolution(position, solNr)
                self.data.AddNewReservoir(position)
            else:
                solution = self.data.GetScreenSolution(position)
                solution.SetProperty("SolutionNr", solNr)
            for component in self.components:
                if component == "Buffer" and record['pH'].strip():
                    name = record[component].strip()
                    ph = float(record['pH'].strip())
                    name += " pH %2.1f" % (ph)
                else:
                    name = record[component].strip()
                    name = name.strip('"')
                unit = record['{'+component+'}']
                conc = record['['+component+']']
                type = component.split()[0]
                if name == "":
                    continue
                if not name in reagents:
                    # generate stock solution if necessary
                    reagent = self.data.AddNewReagent()
                    reagent.SetProperty('name', name)
                    reagent.SetProperty('unit', unit)
                    reagent.SetProperty('type', type)
                    if component == "Buffer":
                        reagent.SetProperty('ph', ph)
                    reagents[name] = reagent.GetAttribute('id')
                # add the component to the screen solution
                try:
                    self.data.GetReservoir(position).selected = True
                except KeyError:
                    print "Well Nr %i not found." % (wellNr)
                    return
                newComp = self.data.AddNewComponent(self.data.GetScreenSolution)
                newComp.SetProperty('SolID', reagents[name])
                newComp.SetProperty('Concentration', conc)
                self.data.GetReservoir(position).selected = False
        
