from NodeData import NodeData, NodeDataType


class IntegerData(NodeData):
    def __init__(self, number = 0):
        self._number = number

    def type(self):
        return NodeDataType("integer", "Integer")

    def number(self):
        return self._number