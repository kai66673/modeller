from PyQt5.QtCore import (QObject, pyqtSignal)

from PortType import PortType
from Serializable import Serializable

from enum import Enum

class ConnectionPolicy(Enum):
    One = 0
    Many = 1

class NodeValidationState(Enum):
    Valid = 0
    Warning = 1
    Error = 2

class NodeDataModel(QObject, Serializable):
    # signals
    dataUpdated = pyqtSignal(int)
    dataInvalidated = pyqtSignal(int)
    computingStarted = pyqtSignal()
    computingFinished = pyqtSignal()

    def __init__(self, nodeStyle = None):
        self._nodeStyle = nodeStyle

    def clone(self):
        raise NotImplementedError("Not implemented method NodeDataModel::clone")

    def name(self):
        raise NotImplementedError("Not implemented method NodeDataModel::name")

    def caption(self):
        raise NotImplementedError("Not implemented method NodeDataModel::caption")

    def captionVisible(self):
        return True

    def portCaption(self, portType, portIndex):
        return ""

    def portCaptionVisible(self, portType, portIndex):
        return False

    def nPorts(self, portType):
        raise NotImplementedError("Not implemented method NodeDataModel::nPorts")

    def dataType(self, portType, portIndex):
        raise NotImplementedError("Not implemented method NodeDataModel::dataType")

    def portOutConnectionPolicy(self, portIndex):
        return ConnectionPolicy.Many

    def setInData(self, nodeData, portIndex):
        raise NotImplementedError("Not implemented method NodeDataModel::setInData")

    def outData(self, portIndex):
        raise NotImplementedError("Not implemented method NodeDataModel::outData")

    def embeddedWidget(self):
        raise NotImplementedError("Not implemented method NodeDataModel::embeddedWidget")

    def resizable(self):
        return False

    def validationState(self):
        return NodeValidationState.Valid

    def validationMessage(self):
        return ""

    def painterDlelegate(self):
        return None
        
    def nodeStyle(self):
        return self._nodeStyle

    def setNodeStyle(self, nodeStyle):
        self._nodeStyle = nodeStyle

    def isValidTypeConvertor(self):
        return self.nPorts(PortType.In) == 1\
               and self.nPorts(PortType.Out) == 1\
               and self.dataType(PortType.In, 0).id != self.dataType(PortType.Out, 0).id
