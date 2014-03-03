#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/demos/gadflypaper/gfe.py
__version__=''' $Id: reporting.py,v 1.5 2007/08/15 17:54:08 schalch Exp $ '''
__doc__=''

#REPORTLAB_TEST_SCRIPT
import sys,os,copy
from reportlab.lib import colors
from reportlab.platypus import *
import reportlab.platypus
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab import rl_settings

PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

class Report:
    """ 
        Report Class:
        Generates a crystallization report using the reportlab library.
        Collects the data and does the rendering.
    """
    
    headerStyle = styles["Heading1"]
    

    """
        parameter parts determines which parts of the reports are printed.
        Its a dictionary with entries given in the fields array.
        parameter tray is a tray class used for the scoring graphics
    """
    def __init__(self, data, parts, tray, filename, tmpDir):
        fields = ["stockSols", "screenSols", "scoreList", "scoreGraphics"]
        self.parts = parts
        self.tray = tray
        self.filename = filename
        self.elements = []
        self.data = data
        self.reportData = ReportData(data, tmpDir)
        self.paraStyle = styles["Normal"]
        self.titleStyle=copy.deepcopy(styles["Heading1"])
        self.titleStyle.fontSize = 30
        self.preStyle = styles["Code"]


    def compile(self):
        if self.parts["scoreList"]:
            scores = self.reportData.GetScoring(False)
            nrScores = len(scores)
            for i in range(nrScores):
                self.header("Scores %i/%i" % (i+1, nrScores))
                self.AddElement(self.reportData.GetHeader())
                self.AddElement(Spacer(0,0.2*inch))
                self.AddElement(scores[i])
        if self.parts["emptyScoringSheet"]:
            if self.parts["scoreList"]:
                self.AddElement(PageBreak())
            scores = self.reportData.GetScoring(True)
            self.header("Scoring Sheet")
            self.AddElement(self.reportData.GetHeader())
            self.AddElement(Spacer(0,0.2*inch))
            self.AddElement(scores[0])
        if self.parts["scoreGraphics"]:
            if self.parts["emptyScoringSheet"]:
                self.AddElement(PageBreak())
            self.header("Score Graphics")
            self.AddElement(self.reportData.GetHeader())
            self.AddElement(Spacer(0,0.2*inch))
            self.AddElement(self.reportData.GetScoreGraphics(self.tray))
        if self.parts["screenSols"]:
            if self.parts["scoreGraphics"]:
                self.AddElement(NextPageTemplate('Landscape'))
                self.AddElement(PageBreak())
            else:
                self.AddElement(NextPageTemplate('Landscape'))
            self.header("Screen Solutions for " + self.data.GetScreenName() + " Screen")
            self.AddElement(Spacer(0,0.2*inch))
            self.AddElement(self.reportData.GetScreen())
            self.AddElement(NextPageTemplate('Portrait'))
        if self.parts["screenVolumes"]:
            if self.parts["screenSols"]:
                self.AddElement(NextPageTemplate('Portrait'))
                self.AddElement(PageBreak())
            else:
                self.AddElement(NextPageTemplate('Portrait'))
            self.header("Screen Solutions for " + self.data.GetScreenName() + " Screen")
            self.AddElement(Spacer(0,0.2*inch))
            self.AddElement(self.reportData.GetSolutions(self.parts["screenVolumes"]))
            self.AddElement(NextPageTemplate('Portrait'))
        if self.parts["stockSols"]:
            if self.parts["screenVolumes"]:
                self.AddElement(PageBreak())
            self.header("Stock Solutions for " + self.data.GetScreenName() + " Screen")
            self.AddElement(Spacer(0,0.2*inch))
            self.AddElement(self.reportData.GetReagentTable())
        try:
            self.go()
            return (True, "Report generated")
        except IOError:
            return (False,"File is not writeable. Please check if it is already open.")

    def myFirstPage(self, canvas, doc):
        canvas.saveState()
        #canvas.setStrokeColorRGB(1,0,0)
        #canvas.setLineWidth(5)
        #canvas.line(66,72,66,PAGE_HEIGHT-72)
        canvas.restoreState()
    
    def myLaterPages(self, canvas, doc):
        #canvas.drawImage("snkanim.gif", 36, 36)
        canvas.saveState()
        #canvas.setStrokeColorRGB(1,0,0)
        #canvas.setLineWidth(5)
        #canvas.line(66,72,66,PAGE_HEIGHT-72)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.5 * inch, "Page %d %s" % (doc.page, "pageinfo"))
        canvas.restoreState()

    def landscape(self, canv, doc):
        canv.rotate(90)
        canv.translate(0,-A4[1])

    def AddElement(self, element):
        self.elements.append(element)

    def AddElements(self, element):
        self.elements.extend(element)
    
    def go(self):
        #self.elements.insert(0,Spacer(0,inch))
        doc = SimpleDocTemplate(self.filename,showBoundary = 0)
        doc.leftMargin = 2 * cm
        doc.bottomMargin = 2 * cm
        doc.rightMargin = 2 * cm
        doc.topMargin = 2 * cm
        doc.width = PAGE_WIDTH - 4 * cm
        doc.height = PAGE_HEIGHT - 4 * cm
        #normal frame as for SimpleFlowDocument
        frameP = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        if not (self.parts["scoreList"] or self.parts["emptyScoringSheet"] or self.parts["scoreGraphics"])\
                    and (self.parts["screenSols"]):
            doc.addPageTemplates([PageTemplate(id='First',frames=frameP, onPage=self.landscape),
                        PageTemplate(id='Landscape',frames=frameP, onPage=self.landscape),
                        PageTemplate(id='Portrait',frames=frameP, onPage=self.myLaterPages),
                        ])
        else:
            doc.addPageTemplates([PageTemplate(id='First',frames=frameP, onPage=self.myFirstPage),
                            PageTemplate(id='Portrait',frames=frameP, onPage=self.myLaterPages),
                            PageTemplate(id='Landscape',frames=frameP, onPage=self.landscape),
                            ])
            
        doc.build(self.elements,onFirstPage=self.myFirstPage)
    
    def header(self, txt, style=headerStyle, klass=Paragraph, sep=0.3):
        s = Spacer(0.2*inch, sep*inch)
        self.elements.append(s)
        para = klass(txt, style)
        self.elements.append(para)

    def p(self, txt):
        return self.header(txt, style=self.paraStyle, sep=0.1)
    
    def pre(self, txt):
        s = Spacer(0.1*inch, 0.1*inch)
        self.elements.append(s)
        p = Preformatted(txt, self.preStyle)
        self.elements.append(p)

    def title(self, txt):
        para = Paragraph(txt,self.titleStyle)
        self.elements.append(para)

#**********************************************************************************

from reportlab.platypus.flowables import Flowable
import Image as pimage
import ImageChops
from reportlab.lib import colors
from reportlab.graphics.shapes import *

class ScoreColorBox(Drawing):
    '''drawing a simple box of a certain size and color'''
    def __init__(self, width, height, color=colors.white):
	self.width=width
	self.height=height
	self.add(Rect(0,0, width, height, 0, 0, fillcolor=color))

class PILImage(Flowable):
    '''An image flowable that is based on PIL. The constructor works with wxBitmaps.'''
    def __init__(self, image):
        self.image = ReportImage(image)
        self.autocrop("white")
        self.size = self.image.getSize()
    
    def wrap(self, aW, aH):
        #self.size = aW-2, aH-2
        return self.size

    def draw(self):
        canvas = self.canv
        w,h = self.size
        canvas.drawImage(self.image, 0,0,w, h)

    def autocrop(self, bgcolor):
        im = self.image._image
        if im.mode != "RGB":
            im = im.convert("RGB")
        bg = pimage.new("RGB", im.size, bgcolor)
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            self.image._image = im.crop(bbox)


class ReportImage:
    def __init__(self, image):
        if type(image) == type(pimage.new("RGB",(1,1))):
            self._image = image
        else:
            size = (image.GetWidth(), image.GetHeight())
            self._image = pimage.fromstring("RGB",size,image.ConvertToImage().GetData())

    def getRGBData(self):
        rgb = self._image.convert('RGB')
        return rgb.tostring()
        
    def getSize(self):
        return self._image.size
        
#**********************************************************************************


class ReportData:
    

    def __init__(self, data, tmpDir):
	self.tmpDir = tmpDir
        self.data = data

    def GetReagentTable(self):
        reagents = self.data.reagents
        tableData = []
        fields = ["name","concentration","unit","reagRemarks"]
        tableData.append(fields)
        for reag in reagents:
            r = []
            for f in fields:
                r.append(reag.GetProperty(f))
            tableData.append(r)
        t = Table(tableData)
        t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
        t.hAlign = 'LEFT'
        return t

    def GetScoreGraphics(self, tray):
        dates = self.data.GetObservationDates()
        tableData = [['',''] for e in range(len(dates)/2+1)]
        #print tableData, len(dates)
	images = []
        for i in range(len(dates)):
            self.data.SetObservationDate(dates[i])
            tray.ClearWells()
	    import pdb
	    trayImage = ReportImage(tray.GetImage((500, 300)))
	    trayImage._image.save(self.tmpDir + 'tmp%i.jpg'%i, "JPEG")
	    images.append(flowables.Image(self.tmpDir + 'tmp%i.jpg'%i, width=200, height=147))
	    tableData[i/2][i%2] = [images[i]]
            #tableData[i/2][i%2] = "image"
        #print tableData
        t = Table(tableData)
        #t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        #    ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
        return t

    def GetScoring(self, emptySheet):
        dates = self.data.GetObservationDates()
        datesPerTable = 7
        if emptySheet:
            nrCols = 6
            dates = [""] * nrCols
        else:
            nrCols = len(dates)
        nrTables = nrCols / datesPerTable
        if nrCols % datesPerTable: nrTables += 1
        tables = []
        for i in range(nrTables):
            dropStyle = copy.deepcopy(styles["Normal"])
            dropStyle.fontSize = 6
            dropStyle.leading = 7
            scoreStyle = copy.deepcopy(styles["Normal"])
            scoreStyle.fontSize = 7
            scoreStyle.leading = 5
            fields = ["Well","Description"]
            tableData = []
            currDates = dates[i*datesPerTable:(i+1) * datesPerTable]
            for date in currDates:
                fields.append(Paragraph(date,scoreStyle))
            tableData.append(fields)
            reservoirs = self.data.reservoirs
            nrDrops = self.data.GetNrDrops()
            for r in reservoirs.values():
                data = []
                position = r.GetProperty("Position")
                apos = self.data.GetAlphabetPosition(position)
                data.append("%s%s"%apos)
                components = self.data.dbBackend.GetChildren(r,"Component")
                solution = 'Reservoir: '
                td = []
                for c in components:
                    solID = c.GetProperty('SolID')
                    reagent = self.data.GetReagent(solID)
                    solution += "%4.2f %s %s, " % (c.GetProperty('Concentration'), \
                        reagent.GetProperty('unit'),\
                        reagent.GetProperty('name'))
                td.append([Paragraph(solution.strip().strip(','),dropStyle)])
                for d in range(nrDrops):
                    drop = self.data.GetDrop((position, d))
                    dcomps = self.data.dbBackend.GetChildren(drop,"DropComponent")
                    comp = 'Drop%d: ' % d
                    for dc in dcomps:
                        if dc.GetProperty("Volume"):
                            comp += "%4.2f ul " % dc.GetProperty("Volume")
                        if dc.GetProperty("Concentration"):
                            comp += "%4.2f mg/ml " % dc.GetProperty("Concentration")
                        comp += dc.GetProperty("Description")
                        if dc.GetProperty("Buffer").strip():
                            comp += " in %s" % dc.GetProperty("Buffer")
                        if dc.GetProperty("Remarks").strip():
                            comp += " (%s)" % dc.GetProperty("Remarks")
                        comp += ", "
                    td.append([Paragraph(comp.strip().strip(','),dropStyle)])
                tnest = Table(td)
                tnest.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0)
                ]))
                data.append(tnest)
                for date in currDates:
                    if emptySheet:
                        data.append("")
                    else:
                        score = ""
                        for d in range(nrDrops):
                            o = self.data.GetObservation(date, (position,d))
                            scores = self.data.GetScores()
                            try:
                                c = scores[o.GetProperty("ScoreValue")].GetProperty("ScoreColor")
                                score += str("<b><font size=\"+3\" color=\"0x%s\">&#8226;</font></b> %d\
                                             <b><font size=\"+3\" color=\"0x%s\">&#8226;</font></b>\n"\
                                             % (c,o.GetProperty("ScoreValue"),c))
                            except KeyError:
                                # print "score not found"
                                pass
                        data.append([Paragraph(score.strip(),scoreStyle)])
                tableData.append(data)
            colWidths = [1*cm]
            dateWidth = 1.3 * cm
            solWidth = PAGE_WIDTH - 5 * cm - len(currDates) * dateWidth
            colWidths.append(solWidth)
            colWidths.extend([dateWidth] * len(currDates))
            t = Table(tableData, colWidths = colWidths, repeatRows = 1)
            t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('FONTSIZE', (1,1), (1,-1), 6),
                ('FONTSIZE', (2,0), (-1,0), 6),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (1,0), (1,-1), 'LEFT')
                ]))
            tables.append(t)
        return tables

    def GetSolutions(self, screenVolume=None):
        nrCols = 2
        dropStyle = copy.deepcopy(styles["Normal"])
        dropStyle.fontSize = 10
        scoreStyle = copy.deepcopy(styles["Normal"])
        scoreStyle.fontSize = 7
        scoreStyle.leading = 5
        fields = ["Well", "Solutions","Well", "Solutions"]
        tableData = []
        tableData.append(fields)
        screenSols = self.data.screenSolutions
        counter = 0
        byReagent = {}
        for r in screenSols.values():
            if counter == 0:
                data = []
            position = r.GetProperty("Position")
            apos = self.data.GetAlphabetPosition(position)
            data.append("%s%s"%apos)
            components = self.data.dbBackend.GetChildren(r,"Component")
            if len(components):
                td = []
                sumVol = 0
                for c in components:
                    solID = c.GetProperty('SolID')
                    reagent = self.data.GetReagent(solID)
                    if not byReagent.has_key(reagent):
                        byReagent[reagent] = []
                    try:
                        vol = c.GetProperty('Concentration') / reagent.GetProperty('concentration') * screenVolume[0]
                    except ZeroDivisionError:
                        td.append([Paragraph("Division by zero. Calculation not possible.",dropStyle)])
                        continue
                    byReagent[reagent].append([vol, position])
                    sumVol += vol
                    solution = "%4.2f %s %4.2f %s %s" % (vol, screenVolume[1], \
                        reagent.GetProperty('concentration'),\
                        reagent.GetProperty('unit'),\
                        reagent.GetProperty('name'))
                    td.append([Paragraph(solution.strip(),dropStyle)])
                td.append([Paragraph("%4.2f %s Water" % (screenVolume[0] - sumVol, screenVolume[1]), dropStyle)])
                tnest = Table(td)
                tnest.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0)
                ]))
                data.append(tnest)
            else:
                data.append("")
            if counter == 0:
                counter =+ 1
            else:
                tableData.append(data)
                counter = 0
        colWidths = [1*cm, 7*cm, 1*cm, 7*cm]
        tByWell = Table(tableData, colWidths = colWidths, repeatRows = 1)
        tByWell.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('FONTSIZE', (1,1), (1,-1), 10),
            ('FONTSIZE', (2,0), (-1,0), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,-1), 'LEFT')
            ]))
        return tByWell


    def GetScoringSystem(self):
        scores = self.data.GetScores()
        tableData = []
        fields = ["Nr", "Description", "Color Code"]
        tableData.append(fields)
        wUnit = int((PAGE_WIDTH - 4 * cm)/30.0)
        for name,score in scores.items():
            data = [name]
            data.append(score.GetProperty("ScoreText"))
            c = score.GetProperty("ScoreColor")
	    d = Drawing(3*wUnit,7)
	    d.add(Rect(0,0,3*wUnit,7, fillColor='#'+c))
            #img = ScoreColorBox(3*wUnit,7, '#'+c)
            data.append(d)
            tableData.append(data)
        colWidths = [1*wUnit, 9*wUnit, 3*wUnit]
        t = Table(tableData, colWidths = colWidths)
        t.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (-1,0), 0.25, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), -2)
                ]))
        return t
    
    def GetHeader(self):
        tableData = [[]]
        description = "<b>Screen: " + str(self.data.GetScreenName()) + "</b>\n\n" \
                      + str(self.data.GetExperimentParams())
        style = copy.deepcopy(styles["Normal"])
        tableData[0].append(Paragraph(description, style))
        #tableData.append("TT")
        tableData[0].append(self.GetScoringSystem())
        colWidths = [(PAGE_WIDTH - 4 * cm)/2] * 2
        t = Table(tableData, colWidths = colWidths)
        t.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,0), 0.25, colors.black),
                ('BOX', (0,0), (-1,0), 0.25, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
                ]))
        return t

    def unhex(self,color):
        col = []
        for i in range(3):
            c = int(color[i*2 : (i+1) * 2], 16)        
            col.append(str(c/255.))
        return col

    def GetScreen(self, screenVolume=None):
        """
            ScreenVolume: list with [volume, volume unit]
        """
        nrCols = self.data.noCols
        nrRows = self.data.noRows

        screenStyle = copy.deepcopy(styles["Normal"])
        #screenStyle.fontSize = 60 / nrCols
        screenStyle.fontSize = 50 / nrCols
        screenStyle.fontName = "Courier"
        screenStyle.leading = 50 / nrCols + 1
        screenStyle.leftIndent = 12
        screenStyle.firstLineIndent = -16
        fields = [""]
        tableData = []

        for i in range(nrCols):
            fields.append(i+1)
        tableData.append(fields)    
        solutions = self.data.screenSolutions
        for i in range(nrRows):
            data = [self.data.GetAlphabetPosition(i*nrCols)[0]]
            for j in range(nrCols):
                position = i * nrCols + j
                solution = self.data.GetScreenSolution(position)
                components = self.data.dbBackend.GetChildren(solution, "Component")
                tableCell = []
                totalVol = 0
                vLineFormat = "%6.2f %s %s (%s %s)"
                cLineFormat = "%6.2f %s %s"
                try:
                    if len(components):
                        for c in components:
                            solID = c.GetProperty('SolID')
                            reagent = self.data.GetReagent(solID)
                            if screenVolume:
                                    v = c.GetProperty('Concentration') / reagent.GetProperty('concentration')\
                                        * screenVolume[0]
                                    totalVol += v
                                    tableCell.append(Paragraph(vLineFormat % (v, \
                                        screenVolume[1],\
                                        reagent.GetProperty('name'),\
                                        reagent.GetProperty('concentration'),\
                                        reagent.GetProperty('unit')),screenStyle))
                            else:
                                tableCell.append(Paragraph(cLineFormat % (c.GetProperty('Concentration'), \
                                    reagent.GetProperty('unit'),\
                                    reagent.GetProperty('name')),screenStyle))
                        if screenVolume:
                            tableCell.append(Paragraph(cLineFormat % (screenVolume[0] - totalVol, \
                                    screenVolume[1],\
                                    "Water"),screenStyle))
                    else:
                        tableCell.append(Paragraph("",screenStyle));
                except ZeroDivisionError:
                    tableCell.append(Paragraph("Division by zero. Calculation not possible.",screenStyle))
                data.append(tableCell)
            tableData.append(data)
        colWidths = [0.5*cm]
        cw = (A4[1] - 4 * cm )/nrCols
        colWidths.extend([cw] * nrCols)
        t = Table(tableData, colWidths = colWidths, repeatRows = 1)
        t.hAlign = 'LEFT'
        t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,1), (-1,-1), 'LEFT')
            ]))
        return t


""" Test code
#####################################################
"""

#from xml_filehandler import OpenFile
#from tray import Tray
#import os, logging
#from wxPython.wx import *

#class TestFrame(wxFrame):
#    def __init__(self):
#        wxFrame.__init__(self, NULL, -1, "Double Buffered Test",
#                         wxDefaultPosition,
#                         size=(500,200),
#                         style=wxDEFAULT_FRAME_STYLE | wxNO_FULL_REPAINT_ON_RESIZE)
#        defFile = os.path.dirname(sys.argv[0]) + "/../../files/Dtd/definition.xml"
#        self.data = OpenFile("V:/Thomas/Screens/pyTray_Files/4n172/041214_MgKClII-4x172agar.exp", defFile)
#        self.tray = Tray(self,self.data)
#        
#    def WritePDF(self):
#        #parts = {"title":"Test Report", "stockSols":1, "scoring":1, "screenSols":1,
#        #         "scoreList":1, "scores":1, "emptyScoringSheet": 1}
#        parts = {"stockSols":1, "screenSols":1,
#                 "scoreList":1, "scoreGraphics":1, "emptyScoringSheet": 1}
#        report = Report(self.data,parts, self.tray, "reportTest.pdf")
#        report.compile()
#        
##        reportData = ReportData(self.data)
##        report.title("Test Setup")
##        report.header("Stock Solutions")
##        report.AddElement(reportData.GetReagentTable())
##        report.header("Scoring System")
##        report.AddElement(reportData.GetScoringSystem())
##        report.AddElement(NextPageTemplate('Landscape'))
##        report.AddElement(PageBreak())
##        report.header("Screen Solutions")
##        report.AddElement(reportData.GetScreen())
##        report.AddElement(NextPageTemplate('Portrait'))
##        report.AddElement(PageBreak())
##        scores = reportData.GetScoring()
##        nrScores = len(scores)
##        for i in range(nrScores):
##            report.header("Scoring Sheet %i/%i" % (i+1, nrScores))
##            report.AddElement(scores[i])

##        #report.header("Scores")
##        #report.AddElement(reportData.GetScoreGraphics(self.tray))
##        report.go()
##        os.system('reportTest.pdf')

#class TrayApp(wxApp):
#    def OnInit(self):
#        wxInitAllImageHandlers() # called so a PNG can be saved
#        frame = TestFrame()
#        frame.Show(true)

#        self.SetTopWindow(frame)
#        frame.WritePDF()
#        return true
        
if __name__ == "__main__":
    logging.basicConfig()
    app = TrayApp(0)
    app.MainLoop()


