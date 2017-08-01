from PyQt5.QtCore import (QPointF)

from NodeGraphicsObject import NodeGraphicsObject
from PortType import PortType
from Serializable import Serializable
from NodeGeometry import NodeGeometry
from NodeState import NodeState

import uuid

class Node(Serializable):
    def __init__(self, dataModel):
        self._id = uuid.uuid4()
        self._nodeDataModel = dataModel
        self._nodeState = NodeState(dataModel)
        self._nodeGeometry = NodeGeometry(dataModel)
        self._nodeGraphicsObject = None

        # self._nodeGeometry.recalculateSize()
        # self._nodeDataModel.dataUpdated.connect(self.onDataUpdated)

    def toJson(self):
        return {
            "id": str(self._id),
            "model": self._nodeDataModel.toJson(),
            "position": {
                "x": self._nodeGraphicsObject.pos().x(),
                "y": self._nodeGraphicsObject.pos().y()
            }
        }

    def restoreFromJson(self, jsonObject):
        self._id = uuid.UUID(jsonObject["id"])
        point = QPointF(jsonObject["position"]["x"],
                        jsonObject["position"]["y"])
        self._nodeGraphicsObject.setPos(point)

    def id(self):
        return self._id

    def reactToPossibleConnection(self, reactingPortType, reactingDataType, scenePoint):
        t = self._nodeGraphicsObject.sceneTransform()
        p = t.inverted().map(scenePoint)
        self._nodeGeometry.setDraggingPosition(p)
        self._nodeGraphicsObject.update()
        self._nodeState.setReaction(NodeState.ReactToConnectionState.REACTING,
                                    reactingPortType,
                                    reactingDataType)

    def resetReactionToConnection(self):
        self._nodeState.setReaction(NodeState.ReactToConnectionState.NOT_REACTING)
        self._nodeGraphicsObject.update()

    def nodeGraphicsObject(self):
        return self._nodeGraphicsObject

    def setGraphicsObject(self, graphics):
        self._nodeGraphicsObject = graphics
        self._nodeGeometry.recalculateSize()

    def nodeGeometry(self):
        return self._nodeGeometry

    def nodeState(self):
        return self._nodeState

    def nodeDataModel(self):
        return self._nodeDataModel

    def propagateData(self, nodeData, inPortIndex):
        self._nodeDataModel.setInData(nodeData, inPortIndex)
        self._nodeGraphicsObject.setGeometryChanged()
        self._nodeGeometry.recalculateSize()
        self._nodeGraphicsObject.update()
        self._nodeGraphicsObject.moveConnections()

    def onDataUpdated(self, index):
        nodeData = self._nodeDataModel.outData(index)
        connections = self._nodeState.connections(PortType.Out, index)
        for c in connections.items():
            c[1].propagateData(nodeData)

    def reactToPossibleConnection(self, reactingPortType, reactingDataType, scenePoint):
        t = self._nodeGraphicsObject.sceneTransform()
        p = t.inverted()[0].map(scenePoint)
        self._nodeGeometry.setDraggingPosition(p)
        self._nodeGraphicsObject.update()
        self._nodeState.setReaction(NodeState.ReactToConnectionState.REACTING, reactingPortType, reactingDataType)

    def resetReactionToConnection(self):
        self._nodeState.setReaction(NodeState.ReactToConnectionState.NOT_REACTING)
        self._nodeGraphicsObject.update()
