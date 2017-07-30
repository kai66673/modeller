class NodeDataType(object):
    def __init__(self, id = "",  name = ""):
        self.id = id
        self.name = name

class NodeData(object):
    def type(self):
        raise NotImplementedError("Not implemented method NodeData::type")
        
    def sameType(self, other):
        return self.type().id == other.type().id
