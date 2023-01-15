import hou
import datetime

from PySide2 import QtGui,QtCore,QtWidgets
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import *
from threading import Timer
from time import sleep
import psutil
      

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
         
        
class myUi(QtWidgets.QMainWindow):
    
    def __init__(self,*args):     

        super(myUi, self).__init__()
        
        self.setMinimumSize(600, 150)
        self.setWindowTitle("Flat Arnold IPR Controller")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.active_IPR = self.findIPRWindow()        
        
        self.timer = RepeatedTimer(1, self.checkIsRendering)       
        
        self.startTime = None
        self.endTime = None
        self.elapsedTime = None
        self.renderCheck = False
        
        self.elapsedHMS = None
        self.renderableRopsDict = None
        
        self.startButton = QPushButton("Start Render", self)
        self.startButton.clicked.connect(self.myStartRender)
        
        self.resumeButton = QPushButton("Resume Render", self)
        self.resumeButton.clicked.connect(self.myResumeRender)
               
        self.pauseButton = QPushButton("Pause Render", self)
        self.pauseButton.clicked.connect(self.myPauseRender)
        
        self.stopButton = QPushButton("Stop Render", self)
        self.stopButton.clicked.connect(self.myStopRender)        
        
        self.ropNodesList = QComboBox(self)
        self.ropNodesList.insertItems(0, self.findRops())
        self.ropNodesList.currentTextChanged.connect(self.setCurrentRenderRop)
        
        self.updateButton = QPushButton("Update Render", self)
        self.updateButton.clicked.connect(self.myUpdateRender)  
        
        self.timeLabel = QLabel("",self)
        self.timeLabel.setText("00:00:00")
        
        gridLay = QGridLayout()
        gridLay.addWidget(self.startButton, 0, 0)
        gridLay.addWidget(self.resumeButton, 0, 1)
        gridLay.addWidget(self.pauseButton, 0, 2)        
        gridLay.addWidget(self.stopButton, 0, 3)
        gridLay.addWidget(self.ropNodesList, 1, 0)
        gridLay.addWidget(self.updateButton, 1, 1)
        gridLay.addWidget(self.timeLabel, 1, 2)
        
        widget = QWidget()
        widget.setLayout(gridLay)
        self.setCentralWidget(widget)
        
        
    def findRops(self):
        
        ropsTypesWhiteList = ["arnold"]
        outContext = hou.node("/out")
        allRops = outContext.children()
        renderableRops = []
        renderableRopsNames = []
        for i in allRops:
            if (i.type().name() in ropsTypesWhiteList):
                renderableRops.append(i)
                renderableRopsNames.append(i.name())                
            if (i.type().name() == "Flat_Arnold"):
                arnoldNode = None
                for j in i.children():
                    if (j.type().name() == "arnold"):
                        renderableRops.append(j)
                        renderableRopsNames.append(i.name())                                           
        self.renderableRopsDict = dict(zip(renderableRopsNames, renderableRops))                 
        return renderableRopsNames                
                
        
    def setCurrentRenderRop(self):
        ropNode = self.renderableRopsDict[self.ropNodesList.currentText()]
        self.active_IPR.setRopNode(ropNode)      
       
        
    def isHickRendering(self):
        
        procs = psutil.process_iter()
        arnoldCpuUsage = None
        
        for i in procs:
            procName = i.name()
            if procName == "hick.exe":
                arnoldCpuUsage = i.cpu_percent()
                break
                
        if arnoldCpuUsage < 10.0:
            return False
        else:
            return True        
             
    
    def findIPRWindow(self):
        myPaneTabs = hou.ui.paneTabs()
    
        for i in myPaneTabs:
            if i.type() == hou.paneTabType.IPRViewer:
                return i                
              
    def myStartRender(self):     
        if (self.active_IPR.isRendering() == False):
            self.active_IPR.startRender()
            self.startTime = datetime.datetime.now()       
        
        self.timeLabel.setText("00:00:00")       
        
        self.endTime = None
        self.elapsedTime = None        
        self.elapsedHMS = None
        self.timer.start()
        
        
    def myResumeRender(self):
        if (self.active_IPR.isPaused() == True):
            self.active_IPR.resumeRender()
            self.startTime = datetime.datetime.now()       
        
            
    def myPauseRender(self):
        if (self.active_IPR.isPaused() == False):
            self.active_IPR.pauseRender()
            self.endTime = datetime.datetime.now()
            
            if(self.elapsedTime == None):
                self.elapsedTime = self.endTime-self.startTime
            
            elif(self.active_IPR.isRendering() == False):
                self.elapsedTime = self.elapsedTime
                
            else:
                self.elapsedTime += self.endTime-self.startTime
            
            self.elapsedHMS = str(self.elapsedTime)[:-7]
            self.timeLabel.setText(self.elapsedHMS)    
        
            
            
    def myStopRender(self):      
        self.active_IPR.killRender()
        self.endTime = datetime.datetime.now()
        self.timer.stop()
        self.renderCheck = False
        
        if(self.elapsedTime == None):
            self.elapsedTime = self.endTime-self.startTime
        
        elif(self.active_IPR.isRendering() == False):
            self.elapsedTime = self.elapsedTime
        
        self.elapsedHMS = str(self.elapsedTime)[:-7]
        self.timeLabel.setText(self.elapsedHMS)

    def myUpdateRender(self):
        self.myStopRender()
        self.myStartRender()
        
        
    def checkIsRendering(self):
    
        if (self.isHickRendering() == False and not self.active_IPR.isPaused()):    
            if self.renderCheck:                
                #print("FINISHED")
                self.myStopRender()
            else:
                #print("LOADING")
                pass
        else:            
            self.renderCheck = True
            #print("RENDERING")

            
mainWin = myUi()
mainWin.show()
