from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsItem

from ConnectionPainter import ConnectionPainter
from GraphicsObjectType import GraphicsObject
from NodeConnectionInteraction import NodeConnectionInteraction
from PortType import PortType


class ConnectionGraphicsObject(QGraphicsObject, GraphicsObject):
    def __init__(self, scene, connection, parent = None):
        super(ConnectionGraphicsObject, self).__init__(parent)
        self._scene = scene
        self._connection = connection

        self._scene.addItem(self)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setAcceptHoverEvents(True)
        self.setZValue(-1.0)

    def type(self):
        return GraphicsObject.Type.Connection

    def connection(self):
        return self._connection

    def boundingRect(self):
        return self._connection.connectionGeometry().boundingRect()

    def setGeometryChanged(self):
        self.prepareGeometryChange()

    def shape(self):
        geom = self._connection.connectionGeometry()
        return ConnectionPainter.getPainterStroke(geom)

    def move(self):
        for portType in [PortType.In, PortType.Out]:
            node = self._connection.getNode(portType)
            if node:
                nodeGraphics = node.nodeGraphicsObject()
                nodeGeom = node.nodeGeometry()
                scenePos = nodeGeom.portScenePosition(self._connection.getPortIndex(portType),
                                                      portType,
                                                      nodeGraphics.sceneTransform())
                connectionPos = self.sceneTransform().inverted()[0].map(scenePos)
                self._connection.connectionGeometry().setEndPoint(portType, connectionPos)
                self.setGeometryChanged()
                self.update()

    def paint(self, painter, option, widget=None):
        painter.setClipRect(option.exposedRect)
        ConnectionPainter.paint(painter, self._connection)

    def locateNodeAt(self, scenePoint, scene, viewTransform):
        items = scene.items(scenePoint, Qt.IntersectsItemShape, Qt.DescendingOrder, viewTransform)
        filteredItems = [item for item in items if item.type() == GraphicsObject.Type.Node]
        if len(filteredItems) > 0:
            return filteredItems[0].node()
        return None

    def mouseMoveEvent(self, event):
        self.prepareGeometryChange()

        node = self.locateNodeAt(event.scenePos(), self._scene, self._scene.views()[0].transform())
        state = self._connection.connectionState()
        state.interactWithNode(node)
        if node:
            node.reactToPossibleConnection(state.requiredPort(), self._connection.dataType(), event.scenePos())
        offset = event.pos() - event.lastPos()
        requiredPort = self._connection.requiredPort()
        if requiredPort != PortType.Invalid:
            self._connection.connectionGeometry().moveEndPoint(requiredPort, offset)
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event):
        self.ungrabMouse()
        event.accept()

        node = self.locateNodeAt(event.scenePos(), self._scene, self._scene.views()[0].transform())
        interaction = NodeConnectionInteraction(node, self._connection, self._scene)
        if node and interaction.tryConnect():
            node.resetReactionToConnection()
        elif self._connection.connectionState().requiresPort():
            self._scene.deleteConnection(self._connection)

    def hoverEnterEvent(self, event):
        self._connection.connectionGeometry().setHovered(True)
        self.update()
        # self._scene.connectionHovered(self._connection, event.screenPos())
        event.accept()

    def hoverLeaveEvent(self, event):
        self._connection.connectionGeometry().setHovered(False)
        self.update()
        event.accept()




