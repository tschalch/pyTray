# This module is used for screen calculation
# Author: Thomas Schalch
# Date: 01/12/2007

class ScreenCalculator:

    def __init__(self, data):
        self.data = data
        InitFactors(self)
        
    def CreateRandomScreen(self):
        pass
        
    def InitFactors(self):
        factors = {}
        reagents = self.data.GetReagents()
        for reagent in reagents:
            id = reagent.GetAttribute("id")
            type = reagent.GetProperty("type")
            minConc = reagent.GetProperty("minConc")
            maxConc = reagent.GetProperty("maxConc")
            if minConc == 0 and maxConc == 0:
                continue
            frequency = reagent.GetProperty("frequency")
            if not factors.has_key(type):
                factors[type] = {}
            factors[type][id] = reagent
            print "Adding reagent:\n%s\n\n" % (reagent.PrettyPrint())
            