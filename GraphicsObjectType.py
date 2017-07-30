from enum import Enum


class GraphicsObject:
    class Type(Enum):
        Unknown = 0
        Node = 1
        Connection = 2

    def type(self):
        return GraphicsObject.Type.Unknown