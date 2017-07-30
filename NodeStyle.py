from PyQt5.QtCore import (QFile, QIODevice, QJsonDocument)
from PyQt5.QtGui import (QColor)

from Style import Style
from StyleCollection import StyleCollection

import modeller_rcc

class NodeStyle(Style):
    def __init__(self,  jsonText=""):
        if not jsonText:
            self.loadJsonFile(":DefaultStyle.json")
        else:
            self.loadJsonText(jsonText)
    
    def setNodeStyle(jsonText):
        style = NodeStyle(jsonText)
        StyleCollection().setNodeStyle(style)
        
    def loadJsonText(self, jsonText):
        self.loadJsonFromByteArray(jsonText.toUtf8())
        
    def loadJsonFile(self, fileName):
        file = QFile(fileName)
        if not file.open(QIODevice.ReadOnly):
            print("Couldn't open file ", fileName)
            return
        self.loadJsonFromByteArray(file.readAll())
    
    def _readColor(self, obj, name):
        valueRef = obj[name]
        if valueRef.isArray():
            colorArray = valueRef.toArray()
            rgb = [0, 0, 0]
            index = 0
            for colorIt in colorArray:
                if index == 3:
                    break
                rgb[index] = colorIt.toInt()
                index += 1
            return QColor(rgb[0], rgb[1],  rgb[2])
        return QColor(valueRef.toString())
        
    def _readFloat(self, obj, name):
        valueRef = obj[name]
        return valueRef.toDouble()
    
    def loadJsonFromByteArray(self, byteArray):
        json = QJsonDocument.fromJson(byteArray)
        topLevelObject = json.object()
        nodeStyleValues = topLevelObject["NodeStyle"]
        obj = nodeStyleValues.toObject()
        # read colors
        self.NormalBoundaryColor        = self._readColor(obj, "NormalBoundaryColor")
        self.SelectedBoundaryColor      = self._readColor(obj, "SelectedBoundaryColor")
        self.GradientColor0             = self._readColor(obj, "GradientColor0")
        self.GradientColor1             = self._readColor(obj, "GradientColor1")
        self.GradientColor2             = self._readColor(obj, "GradientColor2")
        self.GradientColor3             = self._readColor(obj, "GradientColor3")
        self.ShadowColor                = self._readColor(obj, "ShadowColor")
        self.FontColor                  = self._readColor(obj, "FontColor")
        self.FontColorFaded             = self._readColor(obj, "FontColorFaded")
        self.ConnectionPointColor       = self._readColor(obj, "ConnectionPointColor")
        self.FilledConnectionPointColor = self._readColor(obj, "FilledConnectionPointColor")
        self.WarningColor               = self._readColor(obj, "WarningColor")
        self.ErrorColor                 = self._readColor(obj, "ErrorColor")
        # other attributes
        self.PenWidth                   = self._readFloat(obj, "PenWidth")
        self.HoveredPenWidth            = self._readFloat(obj, "HoveredPenWidth")
        self.ConnectionPointDiameter    = self._readFloat(obj, "ConnectionPointDiameter")
        self.Opacity                    = self._readFloat(obj, "Opacity")
        
