# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""
from PyQt5.QtCore import (Qt, QSettings, QByteArray)
from PyQt5.QtGui import (QKeySequence,  QIcon)
from PyQt5.QtWidgets import (QMainWindow,  QAction, QDockWidget)

import modeller_rcc
from GraphicsScene import GraphicsScene
from GraphicsView import GraphicsView

class MainWindow(QMainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        
        self.createActions()
        self.createMenu()
        self.createToolBars()
        self.createDocks()
        
        self.scene = GraphicsScene(self.galleryDock)
        self.view = GraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        self.statusBar().show()
        
        self.settings = QSettings("QxAdvice",  "Modeller")
        self.readSettings()

    def closeEvent(self, event):
        self.writeSettings()
        if self.scene.applicationAboutToClose(self):
            event.accept()
        else:
            event.ignore()

    def readSettings(self):
        self.settings.beginGroup("MainWindow")
        self.restoreGeometry(self.settings.value("geometry", QByteArray()))
        self.restoreState(self.settings.value("windowState", QByteArray()))
        self.settings.endGroup()
        
    def writeSettings(self):
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.endGroup()
    
    def createActions(self):
        self.newAct     = QAction(QIcon(':/images/new.png'), "&New", self,
                                  shortcut=QKeySequence.New, triggered=self.newFile,
                                  statusTip="Create a new file", toolTip="Create a new file")
        self.openAct    = QAction(QIcon(':/images/open.png'), "&Open...", self,
                                  shortcut=QKeySequence.Open, triggered=self.openFile,
                                  statusTip="Open an existing file", toolTip="Open an existing file")
        self.saveAct    = QAction(QIcon(':/images/save.png'), "&Save",  self, 
                                  shortcut=QKeySequence.Save, triggered=self.saveFile,
                                  statusTip="Save current file", toolTip="Save current file")
        self.saveAsAct  = QAction(QIcon(':/images/saveas.png'), "Save &As...", self,
                                  shortcut=QKeySequence.SaveAs, triggered=self.saveFileAs,
                                  statusTip="Save current file as...", toolTip="Save current file as...")
        self.exitAct    = QAction(QIcon(':/images/exit.png'), "E&xit", self,
                                  shortcut="Ctrl+Q", triggered=self.close,
                                  statusTip="Exit the application", toolTip="Exit the application")
        
    def createMenu(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        
    
    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setObjectName("FileToolBar")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addAction(self.saveAsAct)
        
        self.docksToolBar = self.addToolBar("Docks")
        self.docksToolBar.setObjectName("DocksToolBar")
    
    def createDocks(self):
        self.galleryDock = QDockWidget("Gallery",  self)
        self.galleryDock.setObjectName("GalleryDock")
        self.galleryDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.galleryDock)
        
        self.objectsInspectorDock = QDockWidget("Objects Inspector", self)
        self.objectsInspectorDock.setObjectName("ObjectsInspectorDockWidget")
        self.objectsInspectorDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.objectsInspectorDock)
        
        self.propertiesDock = QDockWidget("Properties",  self)
        self.propertiesDock.setObjectName("PropertiesDockWidget")
        self.propertiesDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea,  self.propertiesDock)
        
        toggleAct = self.galleryDock.toggleViewAction()
        toggleAct.setIcon(QIcon(':/images/gallery.png'))
        toggleAct.setToolTip("Toggle visability gallery dock")
        toggleAct.setStatusTip("Toggle visability gallery dock")
        self.docksToolBar.addAction(toggleAct)
        
        toggleAct = self.objectsInspectorDock.toggleViewAction()
        toggleAct.setIcon(QIcon(':/images/inspector.png'))
        toggleAct.setToolTip("Toggle visability inspector dock")
        toggleAct.setStatusTip("Toggle visability inspector dock")
        self.docksToolBar.addAction(toggleAct)
        
        toggleAct = self.propertiesDock.toggleViewAction()
        toggleAct.setIcon(QIcon(':/images/properties.png'))
        toggleAct.setToolTip("Toggle visability properties dock")
        toggleAct.setStatusTip("Toggle visability properties dock")
        self.docksToolBar.addAction(toggleAct)

    def applicationName(self):
        return "Modeller"
    
    def newFile(self):
        self.scene.newDocument(self)
        
    def openFile(self):
        self.scene.openDocument(self)
        
    def saveFile(self):
        self.scene.saveDocument(self)
        
    def saveFileAs(self):
        self.scene.saveDocumentAs(self)
