from NodeDataModel import ConnectionPolicy
from NodeGeometry import NodeGeometry
from PortType import PortType


class NodeConnectionInteraction:
    def __init__(self, node, connection, scene):
        self._node = node
        self._connection = connection
        self._scene = scene

    def canConnect(self):
        typeConversionNeeded = False
        portIndex = -1
        converterModel = None

        requiredPort = self.connectionRequiredPort()
        if requiredPort == PortType.Invalid:
            return (False, typeConversionNeeded, portIndex, converterModel)

        connectionPoint = self.connectionEndScenePosition(requiredPort)
        portIndex = self.nodePortIndexUnderScenePoint(requiredPort,
                                                      connectionPoint)
        if portIndex == -1:
            return (False, typeConversionNeeded, portIndex, converterModel)
        
        if not self.nodePortIsEmpty(requiredPort, portIndex):
            return (False, typeConversionNeeded, portIndex, converterModel)

        connectionDataType = self._connection.dataType()
        modelTarget = self._node.nodeDataModel()
        candidateNodeDataType = modelTarget.dataType(requiredPort, portIndex)

        if connectionDataType.id != candidateNodeDataType.id:
            if requiredPort == PortType.In:
                converterModel = self._scene.registry().getTypeConverter(connectionDataType.id, candidateNodeDataType.id)
                typeConversionNeeded = converterModel != None
                return (typeConversionNeeded, typeConversionNeeded, portIndex, converterModel)
            converterModel = self._scene.registry().getTypeConverter(candidateNodeDataType.id, connectionDataType.id)
            typeConversionNeeded = converterModel != None
            return (typeConversionNeeded, typeConversionNeeded, portIndex, converterModel)

        return (True, typeConversionNeeded, portIndex, converterModel)

    def tryConnect(self):
        (converatable, typeConversionNeeded, portIndex, typeConverterModel) = self.canConnect()
        if not converatable:
            return False

        if typeConversionNeeded:
            requiredPort = self.connectionRequiredPort()
            connectedPort = PortType.In if requiredPort == PortType.Out else PortType.Out

            outNode = self._connection.getNode(connectedPort)
            outNodePortIndex = self._connection.getPortIndex(connectedPort)

            converterNode = self._scene.createNode(typeConverterModel)
            converterNodePos = NodeGeometry.calculateNodePositionBetweenNodePorts(portIndex, requiredPort, self._node,
                                                                                  outNodePortIndex, connectedPort,
                                                                                  outNode, converterNode)
            converterNode.nodeGraphicsObject().setPos(converterNodePos)

            if requiredPort == PortType.In:
                self._scene.createConnection(converterNode, 0, PortType.Invalid, outNode, outNodePortIndex)
                self._scene.createConnection(self._node, portIndex, PortType.Invalid, converterNode, 0)
            else:
                self._scene.createConnection(converterNode, 0, self._node, portIndex)
                self._scene.createConnection(outNode, outNodePortIndex, converterNode, 0)

            self._scene.deleteConnection(self._connection)
            return True

        requiredPort = self.connectionRequiredPort()
        self._node.nodeState().setConnection(requiredPort, portIndex, self._connection)
        self._connection.setNodeToPort(self._node, requiredPort, portIndex)
        self._node.nodeGraphicsObject().moveConnections()

        outNode = self._connection.getNode(PortType.Out)
        if outNode:
            outPortIndex = self._connection.getPortIndex(PortType.Out)
            outNode.onDataUpdated(outPortIndex)

        return True

    def disconnect(self, portToDisconnect):
        portIndex = self._connection.getPortIndex(portToDisconnect)
        state = self._node.nodeState()
        state.getEntries(portToDisconnect)[portIndex].clear()
        self._connection.propagateEmptyData()
        self._connection.clearNode(portToDisconnect)
        self._connection.setRequiredPort(portToDisconnect)

        self._connection.getConnectionGraphicsObject().grabMouse()
        return  True

    def connectionRequiredPort(self):
        return self._connection.connectionState().requiredPort()

    def connectionEndScenePosition(self, portType):
        go = self._connection.getConnectionGraphicsObject()
        geometry = self._connection.connectionGeometry()
        endPoint = geometry.getEndPoint(portType)
        return go.mapToScene(endPoint)

    def nodePortScenePosition(self, portType, portIndex):
        geom = self._node.nodeGeometry()
        p = geom.portScenePosition(portIndex, portType)
        ngo = self._node.nodeGraphicsObject()
        return ngo.sceneTransform().map(p)

    def nodePortIndexUnderScenePoint(self, portType, scenePoint):
        nodeGeom = self._node.nodeGeometry()
        sceneTransform = self._node.nodeGraphicsObject().sceneTransform()
        portIndex = nodeGeom.checkHitScenePoint(portType,
                                                scenePoint,
                                                sceneTransform)
        return portIndex

    def nodePortIsEmpty(self, portType, portIndex):
        nodeState = self._node.nodeState()
        entries = nodeState.getEntries(portType)
        if len(entries[portIndex]) == 0:
            return True
        outPolicy = self._node.nodeDataModel().portOutConnectionPolicy(portIndex)
        return portType == PortType.Out and outPolicy == ConnectionPolicy.Many