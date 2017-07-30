from PyQt5.QtCore import QFile, QIODevice, QJsonDocument
from PyQt5.QtGui import QColor

from Style import Style
from StyleCollection import StyleCollection


class ConnectionStyle(Style):
    def __init__(self,  jsonText=""):
        if not jsonText:
            self.loadJsonFile(":DefaultStyle.json")
        else:
            self.loadJsonText(jsonText)

    def setConnectionStyle(jsonText):
        style = ConnectionStyle(jsonText)
        StyleCollection().setConnectionStyle(style)

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

    def _readBool(self, obj, name):
        valueRef = obj[name]
        return valueRef.toBool()

    def loadJsonFromByteArray(self, byteArray):
        json = QJsonDocument.fromJson(byteArray)
        topLevelObject = json.object()
        nodeStyleValues = topLevelObject["ConnectionStyle"]
        obj = nodeStyleValues.toObject()
        # read colors
        self.ConstructionColor      = self._readColor(obj, "ConstructionColor")
        self.NormalColor            = self._readColor(obj, "NormalColor")
        self.SelectedColor          = self._readColor(obj, "SelectedColor")
        self.SelectedHaloColor      = self._readColor(obj, "SelectedHaloColor")
        self.HoveredColor           = self._readColor(obj, "HoveredColor")
        # other attributes
        self.LineWidth              = self._readFloat(obj, "LineWidth")
        self.ConstructionLineWidth  = self._readFloat(obj, "ConstructionLineWidth")
        self.PointDiameter          = self._readFloat(obj, "PointDiameter")
        self.UseDataDefinedColors   = self._readBool(obj, "UseDataDefinedColors")
