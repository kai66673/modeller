from PyQt5.QtCore import (QPointF, QRectF,  QRect)
from PyQt5.QtGui import (QFont, QFontMetrics, QTransform)

from PortType import PortType
from StyleCollection import StyleCollection
from NodeDataModel import NodeValidationState

import math


class NodeGeometry(object):
    def __init__(self, dataModel):
        self._width = 100
        self._height = 150
        self._inputPortWidth = 70
        self._outputPortWidth = 70
        self._entryHeight = 20
        self._entryWidth = 20
        self._spacing = 20
        self._hovered = False
        self._nSources = dataModel.nPorts(PortType.Out)
        self._nSinks = dataModel.nPorts(PortType.In)
        self._draggingPos = QPointF(-1000, 1000)
        self._dataModel = dataModel
        f = QFont()
        self._fontMetrics = QFontMetrics(f)
        self._boldFontMetrics = QFontMetrics(f)
        self._inputPortWidth = 0
        self._outputPortWidth = 0
        
    def width(self):
        return self._width

    def setWidth(self, w):
        self._width = w

    def height(self):
        return self._height

    def setHeight(self, h):
        self._height = h

    def entryWidth(self):
        return self._entryWidth

    def setEntryWidth(self, w):
        self._entryWidth = w

    def entryHeight(self):
        return self._entryHeight

    def setEntryHeight(self, h):
        self._entryHeight = h

    def spacing(self):
        return self._spacing

    def setSpacing(self, s):
        self._spacing = s

    def hovered(self):
        return self._hovered

    def setHovered(self, h):
        self._hovered = h

    def nSources(self):
        return self._nSources

    def nSinks(self):
        return self._nSinks

    def draggingPos(self):
        return self._draggingPos

    def setDraggingPosition(self,  pos):
        self._draggingPos = pos
        
    def entryBoundingRect(self):
        addon = 0.0
        return QRectF(0 - addon,
                      0 - addon,
                      self._entryWidth + 2 * addon,
                      self._entryHeight + 2 * addon)
                      
    def boundingRect(self):
        nodeStyle = StyleCollection().nodeStyle()
        addon = 4.0 * nodeStyle.ConnectionPointDiameter
        return QRectF(0 - addon,
                      0 - addon,
                      self._width + 2 * addon,
                      self._height + 2 * addon)

    def portWidth(self, portType):
        width = 0
        for i in range(0, self._dataModel.nPorts(portType)):
            name = ''
            if self._dataModel.portCaptionVisible(portType, i):
                name = self._dataModel.portCaption(portType, i)
            else:
                name = self._dataModel.dataType(portType, i).name
            width = max(self._fontMetrics.width(name), width)
        return width
                      
    def recalculateSize(self):
        self._entryHeight = self._fontMetrics.height()

        maxNumOfEntries = max(self._nSinks, self._nSources)
        step = self._entryHeight + self._spacing
        self._height = step * maxNumOfEntries

        w = self._dataModel.embeddedWidget()
        if w:
            self._height = max(self._height, w.height())

        self._height += self.captionHeight()

        self._inputPortWidth  = self.portWidth(PortType.In)
        self._outputPortWidth = self.portWidth(PortType.Out)

        self._width = self._inputPortWidth + self._outputPortWidth + 2 * self._spacing
        
        if w:
            self._width += w.width()

        self._width = max(self._width, self.captionWidth())

        if self._dataModel.validationState() != NodeValidationState.Valid:
            self._width   = max(self._width, self.validationWidth())
            self._height += self.validationHeight() + self._spacing
            
    def recalculateSizeForFont(self, font):
        fontMetrics = QFontMetrics(font)
        boldFont = font
        boldFont.setBold(True)
        boldFontMetrics = QFontMetrics(boldFont)
        if self._boldFontMetrics != boldFontMetrics:
            self._fontMetrics     = fontMetrics
            self._boldFontMetrics = boldFontMetrics
            self.recalculateSize()
            
    def portScenePosition(self, index, portType, t = QTransform()):
        result = QPointF()
        nodeStyle = StyleCollection().nodeStyle()
        step = self._entryHeight + self._spacing
        totalHeight = self.captionHeight()
        totalHeight += step * index
        totalHeight += step / 2.0
        if portType == PortType.Out:
            x = self._width + nodeStyle.ConnectionPointDiameter
            result = QPointF(x, totalHeight)
        elif portType == PortType.In:
            x = 0.0 - nodeStyle.ConnectionPointDiameter
            result = QPointF(x, totalHeight)
        return t.map(result)
        
    def checkHitScenePoint(self, portType, scenePoint, sceneTransform):
        nodeStyle = StyleCollection().nodeStyle()
        result = -1
        if portType == PortType.Invalid:
            return result
        nItems = self._dataModel.nPorts(portType)
        tolerance = 2.0 * nodeStyle.ConnectionPointDiameter
        for i in range(0, nItems):
            pp = self.portScenePosition(i, portType, sceneTransform)
            p = pp - scenePoint
            distance = math.sqrt(QPointF.dotProduct(p, p))
            if distance < tolerance:
                result = i
                break
        return result
        
    def resizeRect(self):
        rectSize = 7
        return QRect(self._width - rectSize,
                     self._height - rectSize,
                     rectSize,
                     rectSize)
                     
    def widgetPosition(self):
        w = self._dataModel.embeddedWidget()
        if w:
            if self._dataModel.validationState() != NodeValidationState.Valid:
                return QPointF(self._spacing + self.portWidth(PortType.In),
                               (self.captionHeight() + self._height - self.validationHeight() - self._spacing - w.height()) / 2.0)
            return QPointF(self._spacing + self.portWidth(PortType.In),
                           (self.captionHeight() + self._height - w.height()) / 2.0)
        return QPointF()
        
    def calculateNodePositionBetweenNodePorts(targetPortIndex, targetPort, targetNode, 
                                              sourcePortIndex, sourcePort, sourceNode, 
                                              newNode):
        converterNodePos = (sourceNode.nodeGraphicsObject().pos() + sourceNode.nodeGeometry().portScenePosition(sourcePortIndex, sourcePort) +
                            targetNode.nodeGraphicsObject().pos() + targetNode.nodeGeometry().portScenePosition(targetPortIndex, targetPort)) / 2.0
        converterNodePos.setX(converterNodePos.x() - newNode.nodeGeometry().width() / 2.0)
        converterNodePos.setY(converterNodePos.y() - newNode.nodeGeometry().height() / 2.0)
        return converterNodePos
        
    def captionHeight(self):
        if not self._dataModel.captionVisible():
            return 0
        name = self._dataModel.caption()
        return self._boldFontMetrics.boundingRect(name).height()
    
    def captionWidth(self):
        if not self._dataModel.captionVisible():
            return 0
        name = self._dataModel.caption()
        return self._boldFontMetrics.boundingRect(name).width()
        
    def validationHeight(self):
        msg = self._dataModel.validationMessage()
        return self._boldFontMetrics.boundingRect(msg).height()
    
    def validationWidth(self):
        msg = self._dataModel.validationMessage()
        return self._boldFontMetrics.boundingRect(msg).width()
