from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLineEdit

from Components.IntegerData import IntegerData
from NodeDataModel import NodeDataModel
from PortType import PortType


class IntegerSourceDataModel(NodeDataModel):
    def __init__(self):
        super(IntegerSourceDataModel, self).__init__()
        self._number = None
        self._lineEdit = QLineEdit()
        self._lineEdit.setValidator(QIntValidator())
        self._lineEdit.setMaximumSize(self._lineEdit.sizeHint())
        self._lineEdit.textChanged.connect(self.onTextEdited)

    def clone(self):
        return IntegerSourceDataModel()

    def name(self):
        return "IntegerSource"

    def caption(self):
        return "Integer Source"

    def captionVisible(self):
        return True

    def portCaption(self, portType, portIndex):
        return ""

    def portCaptionVisible(self, portType, portIndex):
        return False

    def nPorts(self, portType):
        return 1 if portType == PortType.Out else 0

    def dataType(self, portType, portIndex):
        return IntegerData().type()

    def outData(self, portIndex):
        return self._number

    def setInData(self, nodeData, portIndex):
        pass

    def embeddedWidget(self):
        return self._lineEdit

    def onTextEdited(self, txt):
        number, ok = self._lineEdit.text().toInt()
        if ok:
            self._number = IntegerData(number)
            self.emit.dataUpdated(0)
        else:
            self._number = None
            self.emit.dataInvalidated(0)
