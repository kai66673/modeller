from ConnectionGeometry import ConnectionGeometry
from ConnectionState import ConnectionState
from PortType import PortType
from Serializable import Serializable

import uuid

class Connection(Serializable):
    def __init__(self, node, portIndex, portType, node1 = None, portIndex1 = -1):
        self._id = uuid.uuid4()
        self._inNode = None
        self._outNode = None
        self._inPortIndex = -1
        self._outPortIndex = -1
        self._connectionState = ConnectionState()
        self._connectionGeometry = ConnectionGeometry()
        self._connectionGraphicsObject = None

        if portType == PortType.Invalid:
            self.setNodeToPort(node, PortType.In, portIndex)
            self.setNodeToPort(node1, PortType.Out, portIndex1)
        else:
            self.setNodeToPort(node, portType, portIndex)
            self.setRequiredPort(PortType.oppositePort(portType))

    def setNodeToPort(self, node, portType, portIndex):
        if portType == PortType.In:
            self._inNode = node
            self._inPortIndex = portIndex
        elif portType == PortType.Out:
            self._outNode = node
            self._outPortIndex = portIndex
        self._connectionState.setNoRequiredPort()

    def setRequiredPort(self, dragging):
        self._connectionState.setRequiredPort(dragging)
        if dragging == PortType.Out:
            self._outNode = None
            self._outPortIndex = -1
        elif dragging == PortType.In:
            self._inNode = None
            self._inPortIndex = -1

    def connectionGeometry(self):
        return  self._connectionGeometry

    def connectionState(self):
        return self._connectionState

    def id(self):
        return  self._id

    def getConnectionGraphicsObject(self):
        return self._connectionGraphicsObject

    def setGraphicsObject(self, graphics):
        self._connectionGraphicsObject = graphics

    def dataType(self):
        if self._inNode:
            model = self._inNode.nodeDataModel()
            return model.dataType(PortType.In, self._inPortIndex)
        elif self._outNode:
            model = self._outNode.nodeDataModel()
            return model.dataType(PortType.Out, self._outPortIndex)
        # Unreachable
        return None

    def getPortIndex(self, portType):
        if portType == PortType.In:
            return self._inPortIndex
        elif portType == PortType.Out:
            return self._outPortIndex
        return -1

    def getNode(self, portType):
        if portType == PortType.In:
            return self._inNode
        elif portType == PortType.Out:
            return self._outNode
        return  None

    def requiredPort(self):
        return self._connectionState.requiredPort()

    def removeFromNodes(self):
        if self._inNode:
            self._inNode.nodeState().eraseConnection(PortType.In, self._inPortIndex, self._id)
        if self._outNode:
            self._outNode.nodeState().eraseConnection(PortType.Out, self._outPortIndex, self._id)

    def propagateData(self, nodeData):
        if self._inNode:
            self._inNode.propagateData(nodeData, self._inPortIndex)

    def propagateEmptyData(self):
        self.propagateData(None)

    def clearNode(self, portType):
        if portType == PortType.In:
            self._inNode = None
            self._inPortIndex = -1
        elif portType == PortType.Out:
            self._outNode = None
            self._outPortIndex = -1
