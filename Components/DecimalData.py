from NodeData import NodeData, NodeDataType


class DecimalData(NodeData):
    def __init__(self, number = 0.0):
        self._number = number

    def type(self):
        return NodeDataType("decimal", "Decimal")

    def number(self):
        return self._number