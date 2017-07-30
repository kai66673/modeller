class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class StyleCollection(object, metaclass=Singleton):
    _nodeStyle = None
    _connectionStyle = None

    def setNodeStyle(self, nodeStyle):
        self._nodeStyle = nodeStyle

    def nodeStyle(self):
        return self._nodeStyle

    def connectionStyle(self):
        return self._connectionStyle

    def setConnectionStyle(self, connectionStyle):
        self._connectionStyle = connectionStyle
