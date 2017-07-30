from PortType import PortType
from NodeData import NodeDataType
from enum import Enum

class NodeState(object):
    class ReactToConnectionState(Enum):
        REACTING = 0
        NOT_REACTING = 1
        
    def __init__(self, model):
        self._outConnections = []
        for i in range(0, model.nPorts(PortType.Out)):
            emptyDict = {}
            self._outConnections.append(emptyDict)
        self._inConnections = []
        for i in range(0, model.nPorts(PortType.In)):
            emptyDict = {}
            self._inConnections.append(emptyDict)
        self._reaction = NodeState.ReactToConnectionState.NOT_REACTING
        self._reactingPortType = PortType.Invalid
        self._resizing = False
        self._reactingDataType = None
        
    def getEntries(self, portType):
        if portType == PortType.In:
            return self._inConnections
        else:
            return self._outConnections
            
    def connections(self, portType, portIndex):
        return self.getEntries(portType)[portIndex]
        
    def setConnection(self, portType,  portIndex,  connection):
        self.getEntries(portType)[portIndex][connection.id()] = connection
        
    def eraseConnection(self,  portType, portIndex,  id):
        del self.getEntries(portType)[portIndex][id]
        
    def reaction(self):
        return self._reaction
        
    def reactingPortType(self):
        return self._reactingPortType
        
    def reactingDataType(self):
        return self._reactingDataType
        
    def setReaction(self, reaction, reactingPortType = PortType.Invalid, reactingDataType = NodeDataType()):
        self._reaction = reaction
        self._reactingPortType = reactingPortType
        self._reactingDataType = reactingDataType
        
    def isReacting(self):
        return self._reaction == NodeState.ReactToConnectionState.NOT_REACTING
        
    def resizing(self):
        return self._resizing
        
    def setResizing(self, resizing):
        self._resizing = resizing
        
