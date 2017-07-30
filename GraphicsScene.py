from PyQt5.QtWidgets import (QGraphicsScene, QTreeWidget, QTreeWidgetItem, QAbstractItemView)
from PyQt5.QtCore import (QRectF, QUuid, pyqtSignal, QPointF, Qt, QMimeData)

from Components.IntegerSourceDataModel import IntegerSourceDataModel
from Components.DecimalSourceDataModel import DecimalSourceDataModel
from Components.ModuloModel import ModuloModel
from Connection import Connection
from ConnectionGraphicsObject import ConnectionGraphicsObject
from ConnectionStyle import ConnectionStyle
from DataModelRegistry import DataModelRegistry
from Node import Node
from NodeGraphicsObject import NodeGraphicsObject
from NodeStyle import NodeStyle
from PortType import PortType
from StyleCollection import StyleCollection

class GalleryTreeWidget(QTreeWidget):
    def __init__(self, parent = None):
        super(GalleryTreeWidget, self).__init__(parent)

    def mimeTypes(self):
        return ["text/plain"]

    def mimeData(self, Iterable, QTreeWidgetItem=None):
        nodeModelName = Iterable[0].data(0, Qt.UserRole)
        if nodeModelName:
            result = QMimeData()
            result.setText(nodeModelName)
            return result
        return None

class GraphicsScene(QGraphicsScene):
    nodeMoved = pyqtSignal(Node, QPointF)
    nodeHovered = pyqtSignal(Node, QPointF)

    def __init__(self, galleryDock, parent=None):
        super(GraphicsScene, self).__init__(parent)
        self._galleryDock = galleryDock
        self.setSceneRect(QRectF(0, 0, 1500, 1500))
        self._connections = dict()
        self._nodes = dict()
        self._registry = DataModelRegistry()

        # default node style
        self.nodeStyle = NodeStyle()
        StyleCollection().setNodeStyle(self.nodeStyle)

        # default connection style
        self.connectionStyoe = ConnectionStyle()
        StyleCollection().setConnectionStyle(self.connectionStyoe)

        # fill gallery
        self._registry.registerModel("Operations", ModuloModel())
        self._registry.registerModel("Sources", IntegerSourceDataModel())
        self._registry.registerModel("Sources", DecimalSourceDataModel())

        # create gallery Tree
        treeView =  GalleryTreeWidget()
        treeView.header().close()
        treeView.setDragDropMode(QAbstractItemView.DragOnly)
        topLevelItems = {}
        for category in self._registry.categories():
            item =  QTreeWidgetItem(treeView)
            item.setText(0, category)
            topLevelItems[category] = item
        for k, v in self._registry.registeredModelsCategoryAssociation().items():
            parent = topLevelItems[v]
            item =  QTreeWidgetItem(parent)
            item.setText(0, k.caption())
            item.setData(0, Qt.UserRole, k.name())
        treeView.expandAll()
        self._galleryDock.setWidget(treeView)

        # testing
        # self.dataModel = NodeDataModel()
        # self.tttt = NodeGraphicsObject(self, Node(self.dataModel))

    def registry(self):
        return self._registry

    def createNode(self, dataModel):
        n = Node(dataModel.clone())
        ngo = NodeGraphicsObject(self, n)
        n.setGraphicsObject(ngo)
        return n

    def createConnection(self, node, portIndex, portType, node1 = None, portIndex1 = -1):
        connection = Connection(node, portIndex, portType, node1, portIndex1)
        cgo = ConnectionGraphicsObject(self, connection)
        if portType == PortType.Invalid:
            node.nodeState().setConnection(PortType.In, portIndex, connection)
            node.nodeState().setConnection(PortType.Out, portIndex1, connection)
        connection.setGraphicsObject(cgo)
        self._connections[connection.id()] = connection
        return connection

    def deleteConnection(self, connection):
        # self.connectionDeleted(connection)
        # connection.removeFromNodes()
        # del self._connections[connection.id()]
        pass
