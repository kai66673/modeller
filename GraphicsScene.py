from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter
from PyQt5.QtWidgets import (QGraphicsScene, QTreeWidget, QTreeWidgetItem, QAbstractItemView, QMessageBox, QFileDialog)
from PyQt5.QtCore import (QRectF, QUuid, pyqtSignal, QPointF, Qt, QMimeData, QSize, QDir, QFile, QJsonValue,
                          QJsonDocument, QPoint)

from Components.DecimalToIntegerConverterDataModel import DecimalToIntegerConverterDataModel
from Components.IntegerSourceDataModel import IntegerSourceDataModel
from Components.DecimalSourceDataModel import DecimalSourceDataModel
from Components.IntegerToDecimalConverterDataModel import IntegerToDecimalConverterDataModel
from Components.ModuloModel import ModuloModel
from Components.MultiplicationModel import MultiplicationModel
from Connection import Connection
from ConnectionGraphicsObject import ConnectionGraphicsObject
from ConnectionStyle import ConnectionStyle
from DataModelRegistry import DataModelRegistry
from GraphicsObjectType import GraphicsObject
from Node import Node
from NodeGeometry import NodeGeometry
from NodeGraphicsObject import NodeGraphicsObject
from NodePainter import NodePainter
from NodeStyle import NodeStyle
from PortType import PortType
from StyleCollection import StyleCollection

import modeller_rcc

import json
import uuid


class GalleryTreeWidget(QTreeWidget):
    def __init__(self, scene, parent = None):
        super(GalleryTreeWidget, self).__init__(parent)
        self._scene = scene

    def startDrag(self, *args, **kwargs):
        items = self.selectedItems()
        if len(items) == 0:
            return

        nodeModelName = items[0].data(0, Qt.UserRole)
        if not nodeModelName:
            return
        nodeModel = self._scene.registry().nodeDataModel(nodeModelName)
        if not nodeModel:
            return

        tempGeom = NodeGeometry(nodeModel)
        tempGeom.recalculateSizeForFont(self._scene.font())

        nodeStyle = nodeModel.nodeStyle()
        diam = nodeStyle.ConnectionPointDiameter
        pixmap = QPixmap(tempGeom.width() + 2 * diam + 1, tempGeom.height() + 2 * diam + 1)
        painter = QPainter()
        painter.begin(pixmap)
        NodePainter.drawDragRect(painter, tempGeom, nodeModel)
        painter.end()

        mime = QMimeData()
        mime.setData('application/x-modeller-nodemodel', str.encode(nodeModelName))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(diam, diam))
        drag.exec_()

class GraphicsScene(QGraphicsScene):
    nodeMoved = pyqtSignal(Node, QPointF)
    nodeHovered = pyqtSignal(Node, QPointF)

    def __init__(self, galleryDock, parent=None):
        super(GraphicsScene, self).__init__(parent)
        self._modified = False
        self._fileName = ''

        self._galleryDock = galleryDock
        self.setSceneRect(QRectF(0, 0, 1500, 1500))
        self._connections = {}
        self._registry = DataModelRegistry()

        # default node style
        self.nodeStyle = NodeStyle()
        StyleCollection().setNodeStyle(self.nodeStyle)

        # default connection style
        self.connectionStyoe = ConnectionStyle()
        StyleCollection().setConnectionStyle(self.connectionStyoe)

        # fill gallery
        self._registry.registerModel("Operations", QIcon(':Components/images/mod_node.png'), ModuloModel())
        self._registry.registerModel("Operations", QIcon(':Components/images/mul_node.png'), MultiplicationModel())
        self._registry.registerModel("Sources", QIcon(':Components/images/int_src.png'), IntegerSourceDataModel())
        self._registry.registerModel("Sources", QIcon(':Components/images/dec_src.png'), DecimalSourceDataModel())
        self._registry.registerModel("Converters", QIcon(':Components/images/dec_int_cnv.png'),
                                     DecimalToIntegerConverterDataModel(), True)
        self._registry.registerModel("Converters", QIcon(':Components/images/int_dec_cnv.png'),
                                     IntegerToDecimalConverterDataModel(), True)

        # create gallery Tree
        treeView =  GalleryTreeWidget(self)
        treeView.header().close()
        treeView.setDragDropMode(QAbstractItemView.DragOnly)
        treeView.setIconSize(QSize(32, 32))
        topLevelItems = {}
        for category in self._registry.categories():
            item =  QTreeWidgetItem(treeView)
            item.setText(0, category)
            topLevelItems[category] = item
        for k, v in self._registry.registeredModelsCategoryAssociation().items():
            parent = topLevelItems[v]
            item =  QTreeWidgetItem(parent)
            item.setText(0, k[0].caption())
            item.setData(0, Qt.UserRole, k[0].name())
            item.setIcon(0, k[1])
        treeView.expandAll()
        self._galleryDock.setWidget(treeView)

        # testing
        # self.dataModel = NodeDataModel()
        # self.tttt = NodeGraphicsObject(self, Node(self.dataModel))

    def toJson(self):
        nodesJsonArray = []
        connectionJsonArray = []
        for item in self.items():
            if item.type() == GraphicsObject.Type.Node:
                nodesJsonArray.append(item.node().toJson())
            elif item.type() == GraphicsObject.Type.Connection:
                connectionJson = item.connection().toJson()
                if connectionJson:
                    connectionJsonArray.append(connectionJson)

        sceneJson = {}
        sceneJson["nodes"] = nodesJsonArray
        sceneJson["connections"] = connectionJsonArray

        return sceneJson

    def registry(self):
        return self._registry

    def createNode(self, dataModel):
        n = Node(dataModel.clone())
        ngo = NodeGraphicsObject(self, n)
        n.setGraphicsObject(ngo)
        self.setModified()
        return n

    def createConnection(self, node, portIndex, portType, node1 = None, portIndex1 = -1):
        connection = Connection(node, portIndex, portType, node1, portIndex1)
        cgo = ConnectionGraphicsObject(self, connection)
        if portType == PortType.Invalid:
            node.nodeState().setConnection(PortType.In, portIndex, connection)
            node1.nodeState().setConnection(PortType.Out, portIndex1, connection)
        connection.setGraphicsObject(cgo)
        self._connections[connection.id()] = connection
        self.setModified()
        return connection

    def deleteConnection(self, connection):
        # self.connectionDeleted(connection)
        connection.removeFromNodes()
        c = self._connections[connection.id()]
        self.removeItem(c.getConnectionGraphicsObject())
        self.setModified()
        del self._connections[connection.id()]

    def removeNode(self, node):
        for nodeEntries in [node.nodeState().getEntries(PortType.In), node.nodeState().getEntries(PortType.Out)]:
            for connections in nodeEntries:
                cc = [connection[1] for connection in connections.items()]
                for c in cc:
                    self.deleteConnection(c)
        self.removeItem(node.nodeGraphicsObject())

    def clearScene(self):
        self.clear()
        self._connections = {}

    def setModified(self, modified = True):
        self._modified = modified

    def newDocument(self, mainWindow):
        if not self._mayBeSave(mainWindow):
            return False

        self.clearScene()
        self._modified = False
        self._fileName = ''
        return True

    def openDocument(self, mainWindow):
        if not self._mayBeSave(mainWindow):
            return False

        fileName = QFileDialog.getOpenFileName(mainWindow,
                                               "Open dataflow Scene",
                                               QDir.homePath(),
                                               "Flow Scene Files (*.flow)")[0]
        if len(fileName) == 0:
            return False

        try:
            jsonDocument = json.load(open(fileName))

            self.clearScene()
            self._modified = False
            self._fileName = fileName

            nodes = {}
            for nodeJson in jsonDocument["nodes"]:
                modelName = nodeJson["model"]["name"]
                nodeModel = self.registry().nodeDataModel(modelName)
                if not nodeModel:
                    raise "Expected node model named as \"{0}\"".format(modelName)
                node = Node(nodeModel.clone())
                ngo = NodeGraphicsObject(self, node)
                node.setGraphicsObject(ngo)
                node.restoreFromJson(nodeJson)
                nodes[node.id()] = node

            for connectionJson in jsonDocument["connections"]:
                nodeInId = uuid.UUID(connectionJson["in_id"])
                nodeOutId = uuid.UUID(connectionJson["out_id"])
                portIndexIn = connectionJson["in_index"]
                portIndexOut = connectionJson["out_index"]
                nodeIn = nodes.get(nodeInId)
                nodeOut = nodes.get(nodeOutId)
                if nodeIn and nodeOut:
                    self.createConnection(nodeIn, portIndexIn, PortType.Invalid, nodeOut, portIndexOut)

            self._modified = False

        except:
            QMessageBox.warning(mainWindow, mainWindow.applicationName(),
                                "Loading dataflow Scene from file \"{0}\" failed".format(fileName))
            return False

        return True

    def saveDocument(self, mainWindow):
        if len(self._fileName) == 0:
            fileName = QFileDialog.getSaveFileName(mainWindow,
                                                   "Save dataflow Scene",
                                                   QDir.homePath(),
                                                   "Flow Scene Files (*.flow)")[0]
            if len(fileName) == 0:
                return False
            return self._saveTo(fileName, mainWindow)
        return self._saveTo(self._fileName, mainWindow)

    def saveDocumentAs(self, mainWindow):
        fileName = QFileDialog.getSaveFileName(mainWindow,
                                               "Save dataflow Scene",
                                               QDir.homePath(),
                                               "Flow Scene Files (*.flow)")[0]
        if len(fileName) == 0:
            return False
        return self._saveTo(fileName, mainWindow)

    def _mayBeSave(self, mainWindow):
        if not self._modified:
            return True

        ret = QMessageBox.warning(mainWindow, mainWindow.applicationName(),
                                  "Data was Changed.\nSave Changes?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Discard:
            return True
        elif ret == QMessageBox.Save:
            return self.saveDocument(mainWindow)

        return False

    def applicationAboutToClose(self, mainWindow):
        return self._mayBeSave(mainWindow)

    def _saveTo(self, fileName, mainWindow):
        try:
            with open(fileName, "w") as file:
                json.dump(self.toJson(), file, indent = 2)
        except:
            QMessageBox.warning(mainWindow, mainWindow.applicationName,
                                "Saving dataflow Scene to file \"{0}\" failed".format(fileName))
            return False

        self._fileName = fileName
        self._modified = False
        return True

