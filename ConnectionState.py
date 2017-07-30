from PortType import PortType


class ConnectionState:
    def __init__(self, portType = PortType.Invalid):
        self._requiredPort = portType
        self._lastHoveredNode = None

    def setRequiredPort(self, end):
        self._requiredPort = end

    def requiredPort(self):
        return self._requiredPort

    def requiresPort(self):
        return self._requiredPort != PortType.Invalid

    def setNoRequiredPort(self):
        self._requiredPort = PortType.Invalid

    def interactWithNode(self, node):
        if node is None:
            self.resetLastHoveredNode()
        else:
            self._lastHoveredNode = node

    def setLastHoveredNode(self, node):
        self._lastHoveredNode = node

    def resetLastHoveredNode(self):
        if self._lastHoveredNode:
            self._lastHoveredNode.resetReactionToConnection()
        self._lastHoveredNode = None