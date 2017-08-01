from PyQt5.QtWidgets import QGraphicsView, QAction
from PyQt5.QtGui import (QColor, QPen)
from PyQt5.QtCore import (Qt, QLineF)

import math

from GraphicsObjectType import GraphicsObject


class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(GraphicsView, self).__init__(scene,  parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QColor(53, 53, 53))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)

        self._clearSelectionAction = QAction("Clear Selection", self,
                                             shortcut=Qt.Key_Escape,
                                             triggered=self.scene().clearSelection)
        self._deleteSelectionAction = QAction("Delete Selection", self,
                                              shortcut=Qt.Key_Delete,
                                              triggered=self.deleteSelectedNodes)
        self.addAction(self._clearSelectionAction)
        self.addAction(self._deleteSelectionAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.setAccepted(True)
            self.update()

    def dropEvent(self, event):
        event.acceptProposedAction()
        nodeDataModel = self.scene().registry().nodeDataModel(event.mimeData().text())
        if nodeDataModel:
            node = self.scene().createNode(nodeDataModel)
            pos = event.pos()
            posView = self.mapToScene(pos)
            node.nodeGraphicsObject().setPos(posView)

    def dragMoveEvent(self, event):
        pass

    def _scaleUp(self):
        step   = 1.2
        factor = math.pow(step, 1.0)
        t = self.transform()
        if t.m11() > 2.0:
            return
        self.scale(factor,  factor)
        
    def _scaleDown(self):
        step   = 1.2
        factor = math.pow(step, -1.0)
        self.scale(factor,  factor)
    
    def wheelEvent(self, event):
        delta = event.angleDelta()
        if delta.y() == 0:
            event.ignore()
            return
        d = delta.y() / abs(delta.y())
        if d > 0.0:
            self._scaleUp()
        else:
            self._scaleDown()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        QGraphicsView.keyPressEvent(self, event)
    
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        QGraphicsView.keyReleaseEvent(self, event)
        
    def _drawGrid(self, painter, gridStep):
        windowRect = self.rect()
        tl = self.mapToScene(windowRect.topLeft())
        br = self.mapToScene(windowRect.bottomRight())
        left   = math.floor(tl.x() / gridStep - 0.5)
        right  = math.floor(br.x() / gridStep + 1.0)
        bottom = math.floor(tl.y() / gridStep - 0.5)
        top    = math.floor (br.y() / gridStep + 1.0)
        for xi in range(int(left),  int(right) + 1):
            painter.drawLine(QLineF(xi * gridStep, bottom * gridStep, xi * gridStep, top * gridStep))
        for yi in range(int(bottom),  int(top) + 1):
            painter.drawLine(QLineF(left * gridStep, yi * gridStep, right * gridStep, yi * gridStep))

    def drawBackground(self, painter, r):
        QGraphicsView.drawBackground(self, painter, r)
        painter.setPen(QPen(QColor(60, 60, 60),  1.0))
        self._drawGrid(painter, 8)
        painter.setPen(QPen(QColor(25, 25, 25),  1.0))
        self._drawGrid(painter, 80)

    def deleteSelectedNodes(self):
        for item in self.scene().selectedItems():
            if item.type() == GraphicsObject.Type.Node:
                self.scene().removeNode(item.node())

        for item in self.scene().selectedItems():
            self.scene().deleteConnection(item.connection())
