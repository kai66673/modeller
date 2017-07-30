from PyQt5.QtCore import Qt, QPoint, QSize, QSizeF
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QGraphicsObject, QGraphicsItem, QGraphicsDropShadowEffect, QGraphicsProxyWidget)

from GraphicsObjectType import GraphicsObject
from NodeConnectionInteraction import NodeConnectionInteraction
from NodeDataModel import ConnectionPolicy
from NodePainter import NodePainter
from PortType import PortType
from StyleCollection import StyleCollection


class NodeGraphicsObject(QGraphicsObject, GraphicsObject):
    def __init__(self, scene,  node,  parent = None):
        super(NodeGraphicsObject, self).__init__(parent)
        self._scene = scene
        self._node = node
        self._proxyWidget = None

        self._scene.addItem(self)
        self.setFlag(QGraphicsItem.ItemDoesntPropagateOpacityToChildren, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self._locked = False
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        nodeStyle = StyleCollection().nodeStyle()
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(4, 4)
        effect.setBlurRadius(20)
        effect.setColor(nodeStyle.ShadowColor)
        self.setGraphicsEffect(effect)
        
        self.setOpacity(nodeStyle.Opacity)
        self.setAcceptHoverEvents(True)
        self.setZValue(0)

        self.embedQWidget()

        self.xChanged.connect(self.onMoveSlot)
        self.yChanged.connect(self.onMoveSlot)

    def type(self):
        return GraphicsObject.Type.Node

    def node(self):
        return self._node

    def embedQWidget(self):
        w = self._node.nodeDataModel().embeddedWidget()
        if w:
            self._proxyWidget = QGraphicsProxyWidget(self)
            self._proxyWidget.setWidget(w)
            self._proxyWidget.setPreferredWidth(5)
            geom = self._node.nodeGeometry()
            geom.recalculateSize()
            self._proxyWidget.setPos(geom.widgetPosition())
            self.update()
            self._proxyWidget.setOpacity(1.0)
            self._proxyWidget.setFlag(QGraphicsItem.ItemIgnoresParentOpacity)

    def boundingRect(self):
        return self._node.nodeGeometry().boundingRect()

    def setGeometryChanged(self):
        self.prepareGeometryChange()

    def moveConnections(self):
        nodeState = self._node.nodeState()

        connectionEntriesList = [nodeState.getEntries(PortType.In), nodeState.getEntries(PortType.In)]
        for connectionEntries in connectionEntriesList:
            for connections in connectionEntries:
                for c in connections.items():
                    c[1].getConnectionGraphicsObject().move()

    def lock(self, locked):
        self._locked = locked
        self.setFlag(QGraphicsItem.ItemIsMovable, not locked)
        self.setFlag(QGraphicsItem.ItemIsFocusable, not locked)
        self.setFlag(QGraphicsItem.ItemIsSelectable, not locked)

    def paint(self, painter, option, w = None):
        painter.setClipRect(option.exposedRect)
        NodePainter.paint(painter, self._node, self._scene)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            self.moveConnections()
        return QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        if self._locked:
            return

        if not self.isSelected() and not (event.modifiers() & Qt.ControlModifier):
            self._scene.clearSelection()

        nodeGeometry = self._node.nodeGeometry()
        nodeState = self._node.nodeState()

        portTypes = [PortType.In, PortType.Out]
        for portToCheck in portTypes:
            portIndex = nodeGeometry.checkHitScenePoint(portToCheck,
                                                        event.scenePos(),
                                                        self.sceneTransform())
            if portIndex != -1:
                connections = nodeState.connections(portToCheck, portIndex)
                if len(connections) != 0 and portToCheck == PortType.In:
                    for c in connections.items():
                        interaction = NodeConnectionInteraction(self._node, c[1], self._scene)
                        interaction.disconnect(portToCheck)
                        break
                else:
                    outPolicy = self._node.nodeDataModel().portOutConnectionPolicy(portIndex)
                    if len(connections) != 0 and portToCheck == PortType.Out and outPolicy == ConnectionPolicy.One:
                        for c in connections.items():
                            self._scene.deleteConnection(c[1])
                            break
                    connection = self._scene.createConnection(self._node, portIndex, portToCheck)
                    self._node.nodeState().setConnection(portToCheck, portIndex, connection)
                    connection.getConnectionGraphicsObject().grabMouse()

        pos = event.pos()
        geom = self._node.nodeGeometry()
        state = self._node.nodeState()
        if geom.resizeRect().contains(QPoint(pos.x(), pos.y())):
            state.setResizing(True)

    def mouseMoveEvent(self, event):
        geom = self._node.nodeGeometry()
        state = self._node.nodeState()

        if state.resizing():
            diff = event.pos() - event.lastPos()
            w = self._node.nodeDataModel().embeddedWidget()
            if w:
                self.prepareGeometryChange()
                oldSize = w.size()
                oldSize += QSize(diff.x(), diff.y())
                w.setFixedSize(oldSize)
                sizeF = QSizeF(oldSize.width(), oldSize.height())
                self._proxyWidget.setMinimumSize(sizeF)
                self._proxyWidget.setMaximumSize(sizeF)
                self._proxyWidget.setPos(geom.widgetPosition())
                geom.recalculateSize()
                self.update()
                self.moveConnections()
                event.accept()
        else:
            QGraphicsObject.mouseMoveEvent(self, event)
            if event.lastPos() != event.pos():
                self.moveConnections()
            event.ignore()

        r = self.scene().sceneRect()
        r = r.united(self.mapToScene(self.boundingRect()).boundingRect())
        self.scene().setSceneRect(r)

    def mouseReleaseEvent(self, event):
        state = self._node.nodeState()
        state.setResizing(False)
        QGraphicsObject.mouseReleaseEvent(self, event)
        self.moveConnections()

    def hoverEnterEvent(self, event):
        overlapItems = self.collidingItems()
        for item in overlapItems:
            if item.zValue() > 0.0:
                item.setZValue(0.0)
        self.setZValue(1.0)

        self._node.nodeGeometry().setHovered(True)
        self.update()
        # self._scene.nodeHovered(self._node, event.screenPos())
        event.accept()

    def hoverLeaveEvent(self, event):
        self._node.nodeGeometry().setHovered(False)
        self.update()
        # self._scene.nodeHoverLeft(self._node)
        event.accept()

    def hoverMoveEvent(self, event):
        pos = event.pos()
        geom = self._node.nodeGeometry()
        if geom.resizeRect().contains(QPoint(pos.x(), pos.y())):
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        else:
            self.setCursor(QCursor())
        event.accept()

    def mouseDoubleClickEvent(self, event):
        QGraphicsItem.mouseDoubleClickEvent(self, event)
        self._scene.nodeDoubleClicked(self._node)

    def onMoveSlot(self):
        self._scene.nodeMoved.emit(self._node, self.pos())

        
