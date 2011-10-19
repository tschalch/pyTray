
import controller
import wx
import dataStructures.user_data
import os, sys, random, traceback
from gui.error_window import ErrorHandler

# reroute the user config file
dataStructures.user_data.configFile =  dataStructures.user_data.apdir + "\\testuser.pyTray"

# setup paths
files = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0]))+"/files/test")
results = open(os.path.abspath(files + "/testresults.txt"), 'w')

# test parent classes performing different kinds of checks

class Test:

    def __init__(self, datafile = None):
        self.contlr = None
        if datafile:
            self.datafile = os.path.abspath(files + datafile)
        else:
            self.datafile = os.path.abspath(files + "/test.exp")
        
    def StartGui(self):
        results.write("Starting gui ... ")
        if not self.contlr:
            self.contlr = controller.Controller(self.datafile)
        self.data = self.contlr.data
        try:
            frame = self.contlr.Start()
        except:
            results.write("Starting tray failed\n")
            print sys.exc_info()
            raise
        results.write("OK\n")
        return frame

    def GetData(self):
        results.write("Reading data ... ")
        self.contlr = controller.Controller(self.datafile)
        results.write("OK\n")
        return self.contlr.data


    def Run(self):
        pass



class TestObservations(Test):

    def Run(self):
        frame = self.StartGui()
        results.write("Adding new observation time point ...")
        results.write(self.data.GetSummary())
        obspanel = frame.xtal_panel.obsPanel
        obspanel.AddObservation(None,"newDate")
        results.write(self.data.GetSummary())
        results.write("OK\n")
        #adding observations
        import gui.tray as traymodule
        results.write("Adding single observations ...")
        self.data.drops[(0,0)].selected = True
        scorecombo = frame.xtal_panel.obsPanel.score_combo
        tray = frame.xtal_panel.tray
        choices = frame.xtal_panel.obsPanel.choices
        remarksbox = frame.xtal_panel.obsPanel.remark_box
        for i in range(self.data.noWells):
            scorecombo.SetValue(choices[i%len(choices)])
            obspanel.SetScore(None)
            remarksbox.SetValue("Test remarks")
            obspanel.SetRemarks(None)
            tray.Move(traymodule.MV_FORWARDS)
        self.data.Save(os.path.abspath(files + "/test_obs.exp"))
        results.write("OK\n")
        results.write("Deleting new observation ...")
        obspanel.DeleteObservation(None,False)
        results.write("OK\n")
        results.write(self.data.GetSummary())
        frame.Destroy()
        

class TestGrids(Test):
    
    def Run(self):
        frame = self.StartGui()
        results.write("Testing reservoir grid ... \n")
        self.data.drops[(random.randint(0, self.data.noWells-1),\
            random.randint(0, self.data.noDrops-1))].selected = True
        grids = [frame.xtal_panel.reservoir_grid,
                frame.xtal_panel.drop_grid,
                frame.screen_panel.composition_grid,
                frame.stock_panel.stock_grid,
                frame.score_panel.score_grid]
        values = [["5","0.1","","TestRemark"],
                ["testsample","5","4","TES", "TestRemark"],
                ["3","1","M","test remark"],
                ["TestReagent","3","M","TestType","4.4","3.4","3","1","110","30","TestRemark"],
                ["11","testscore","000000"]]
                
        for i in range(len(grids)):
            grid = grids[i]
            gridData = grid.GetTable()
            gridData.ResetView()
            results.write("Initial table contents:\n")
            results.write(gridData.GetAsString())
            self.TestGridFunctions(grid,values[i])
        frame.Destroy()

    def TestGridFunctions(self, grid, values):
        results.write("Testing grid functions ... \n")
        results.write("    Adding row ... \n")
        # adding rows
        grid.OnAdd(None)
        # setting values
        results.write("    Setting values ... \n")
        newRow = grid.GetNumberRows() - 2
        for col in range(grid.GetNumberCols()):
            grid.SetCellValue(newRow, col, values[col])
        results.write(grid.GetAsString())
         # deleting rows
        results.write("    Deleting random row ... \n")
        grid.SelectRow(random.randint(0, grid.GetNumberRows()-2))
        grid.OnDelete(None)
        results.write(grid.GetAsString())

class TestNewScreens(Test):
    
    def Run(self):
        results.write("New Screen from scratch ... ")
        name = "Testscreen"
        noRows = random.randint(1,12)
        noCols = random.randint(1,12)
        noDrops = random.randint(1,3)
        newScreen = {"ScreenName": name, "NoRows": noRows, \
                    "NoCols":noCols, "NoDrops":noDrops}
        contlr = controller.Controller(self.datafile)
        data = contlr.NewTray(None,(None,newScreen))
        newFile = os.path.abspath(files + "/newScreen.exp")
        data.Save(newFile)
        data.Close()
        data = contlr.GetTrayData(None,newFile)
        results.write("OK\n")
        results.write(data.GetSummary())
        data.Close()
        results.write("New Screen from template ... ")
        source = contlr.data
        newScreen = {"ScreenName": source.GetScreenName(), "NoRows": source.noRows, \
                    "NoCols":source.noCols, "NoDrops":source.noDrops}       
        data = contlr.NewTray(None,(source,newScreen))
        noWells = source.noCols * source.noRows
        newFile = os.path.abspath(files + "/newScreenTempl.exp")
        data.Save(newFile)
        data.Close()
        data = contlr.GetTrayData(None,newFile)
        results.write(data.GetSummary())
        results.write("OK\n")
        results.write("Testing reservoir initialization ... ")
        data.InitReservoirsFromScreen()
        reservoir = data.GetReservoir(random.randint(0, noWells-1)).PrettyPrint()
        results.write("OK\n")
        results.write(reservoir)
        data.Close()
        source.Close()

class TestDataStructure(Test):
    
    def Run(self):
        results.write("Testing data structures\n\n")
        data = self.GetData()
        results.write(data.GetSummary())
        imagefile = os.path.abspath(files + "/test.jpg")
        # select observation date and drop
        dates = data.GetObservationDates()
        data.SetObservationDate(dates[random.randint(0,len(dates)-1)])
        data.drops[(random.randint(0, data.noWells-1),\
            random.randint(0, data.noDrops-1))].selected = True
        # test image operations
        results.write("Adding image ... ")
        noImgs = len(data.GetImages())
        data.AddImage(imagefile)
        if len(data.GetImages()) == (noImgs + 1):
            results.write("OK\n")
        else:
            results.write("FAILED\n")
        results.write("Deleting image ... ")
        try:
            image = data.GetImages()[random.randint(0,noImgs-1)]
            data.DeleteImage(image)
            if len(data.GetImages()) == (noImgs):
                results.write("OK\n")
            else:
                results.write("FAILED\n")
        except Exception, e:
            print "Delete image failed"
            data.Close()
            raise
        # test observations
        results.write("Adding observation date ... ")
        obsname = "TestObservation"
        data.AddNewObservation(obsname)
        if data.GetObservationDates().count(obsname) > 0:
            results.write("OK\n")
        else:
            results.write("FAILED\n")
        results.write("Deleting observation date ... ")
        data.DeleteObservation(obsname)        
        if data.GetObservationDates().count(obsname) > 0:
            results.write("FAILED\n")
        else:
            results.write("OK\n")
        # test screen solutions
        results.write("Deleting screen solution and undo ... ")
        data.DeleteScreenSolutions()
        data.Undo()
        results.write("OK\n")
        # test sorting
        results.write("Sorting stock solutions by name ... ")
        data.SortReagents("name")
        results.write("OK\n")
        # test saving
        results.write("Saving data ... ")
        data.Save(os.path.abspath(files + "/test_out.exp"))
        results.write("OK\n")
        #test exporting
        results.write("Exporting data for analysis ... ")
        data.SaveAnalysisData(os.path.abspath(files + "/test_analysis.cvs"))
        results.write("OK\n")
        results.write("Exporting data for Simplex analysis ... ")
        data.SaveSimplexData(os.path.abspath(files + "/test_simplex.txt"))
        results.write("OK\n")
        results.write(data.GetSummary())
        data.Close()

class TestReporting(Test):

    def Run(self):
        from dataStructures.reporting import Report
        results.write("Testing data structures\n\n")
        frame = self.StartGui()
        results.write("OK\n")
        results.write(self.data.GetSummary())
        results.write("Testing reporting ... ")
        partList = ["scoreList", "emptyScoringSheet","scoreGraphics","screenSols", "stockSols"]
        parts = {}
        for part in partList:
            #if part == "emptyScoringSheet":
            if part:
                parts[part] = 1
            else:
                parts[part] = 0
        parts["screenVolumes"] = (10,"ml")
        path = os.path.abspath(files + "/test.pdf")
        try:
            report = Report(self.data,parts, frame.xtal_panel.tray, path)
            gen = report.compile()
            os.startfile(path)
        except:
            print "Reporting failed"
            print sys.exc_info()
            raise
        results.write("OK\n")
        frame.Destroy()

class TestScreenGenerator(Test):
    def Run(self):
        from util.screen_generator import ScreenGenerator
        results.write("***********\nTesting Screen Generator ... \n")
        results.write("Open Test file with stock solution ... ")
        data = self.GetData()
        #frame = self.StartGui()
        results.write("OK\n")
        results.write(data.GetSummary())
        results.write("Starting ScreenGenerator ... ")
        generator = ScreenGenerator(data)
        results.write("OK ... ")
        results.write("Generating random screen ... ")
        generator.CreateRandomScreen()
        results.write("OK ... ")
        frame = self.StartGui()

class TestConverter(Test):
    def Run(self):
        results.write("*************\nTesting Converter ... \n")
        results.write("New Screen from scratch ... ")
        name = "Hampton Crystal Screen - Test Conversion"
        noRows = 4
        noCols = 6
        noDrops = 1
        newScreen = {"ScreenName": name, "NoRows": noRows, \
                    "NoCols":noCols, "NoDrops":noDrops}
        contlr = controller.Controller(None)
        data = contlr.NewTray(None,(None,newScreen))
        from util.converter import Converter
        converter = Converter(files + "/hampton_crystal_screen2_25-48.csv", data)
        results.write("New screen before import:\n")
        results.write(data.GetSummary())
        converter.convert()
        results.write("Screen after import:\n")
        results.write(data.GetSummary())
        newFile = os.path.abspath(files + "/CrystalScreenConverted.exp")
        data.Save(newFile)
        # testing import for stock solution only
        results.write("Importing stock solutions only...\n")
        converter = Converter(files + "/simplex_Stocks.csv", data)
        converter.convertStocks()
        results.write("Screen after import:\n")
        results.write(data.GetSummary())
        newFile = os.path.abspath(files + "/CrystalScreenStocksConverted.exp")
        data.Save(newFile)
        # testing for screen solutions from simplex output
        results.write("Importing simplex screen solutions only...\n")
        converter = Converter(files + "/simplex_screen.csv", data)
        converter.convertSimplexScreen()
        results.write("Screen after import:\n")
        results.write(data.GetSummary())
        newFile = os.path.abspath(files + "/CrystalScreenSimplexConverted.exp")
        data.Save(newFile)
        # removing unused reagents
        results.write("Removing unused reagents...\n")
        data.RemoveUnusedReagents()
        results.write(data.GetSummary())
        data.Close()
        self.datafile = newFile
        #data = contlr.GetTrayData(None,newFile)
        frame = self.StartGui()
 
class TestTwainCamera(Test):

    def Run(self):
        results.write("**********\nTesting Twain Camera ... \n")
        # test class for twain module
        #from util.twain_camera import TwainFrame
        #frame = TwainFrame(None, -1, "Simple TWAIN Demo")
        #frame.Show(True)
        # pytray camera module
        frame = self.StartGui()
        obspanel = frame.xtal_panel.obsPanel
        self.data.drops[(0,0)].selected = True
        obspanel.StartVideo(None)
        #obspanel.GrabImage()

class Testing:

    def __init__(self, testmodule):
        try:
            if testmodule == "all":
                for module in testmodules:
                    testmodules[module].Run()
            elif testmodules.has_key(testmodule):
                testmodules[testmodule].Run()
        except:
            results.write(traceback.format_exc())
            print traceback.format_exc()



testmodules = { "data":TestDataStructure(), 
                "jdata":TestDataStructure("/jtest.exp"),
                "report":TestReporting(),
                "new":TestNewScreens(),
                "grids":TestGrids(),
                "obs":TestObservations(),
                "convert": TestConverter(),
                "twain":TestTwainCamera(),
                "generate":TestScreenGenerator("/StockSolutions.exp")
                }

