from enum import Enum

class PortType(Enum):
    Invalid = 0
    In = 1
    Out = 2

    @staticmethod
    def oppositePort(port):
        if port == PortType.In:
            return PortType.Out
        if port == PortType.Out:
            return PortType.In
        return PortType.Invalid

class Port:
    def __init__(self, t=PortType.Invalid, i=-1):
        self.type = t
        self.index = i
        
    def indexIsValid(self):
        return self.index != -1
        
    def portTypeIsValid(self):
        return self.type != PortType.Invalid

