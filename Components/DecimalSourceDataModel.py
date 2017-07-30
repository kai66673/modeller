from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QLineEdit

from Components.DecimalData import DecimalData
from NodeDataModel import NodeDataModel
from PortType import PortType
from StyleCollection import StyleCollection


class DecimalSourceDataModel(NodeDataModel):
    def __init__(self):
        super(DecimalSourceDataModel, self).__init__(StyleCollection().nodeStyle())
        self._number = None
        self._lineEdit = QLineEdit()
        self._lineEdit.setValidator(QDoubleValidator())
        self._lineEdit.setMaximumSize(self._lineEdit.sizeHint())
        self._lineEdit.textChanged.connect(self.onTextEdited)

    def clone(self):
        return DecimalSourceDataModel()

    def name(self):
        return "DecimalSource"

    def caption(self):
        return "Decimal Source"

    def captionVisible(self):
        return True

    def portCaption(self, portType, portIndex):
        return ""

    def portCaptionVisible(self, portType, portIndex):
        return False

    def nPorts(self, portType):
        return 1 if portType == PortType.Out else 0

    def dataType(self, portType, portIndex):
        return DecimalData().type()

    def outData(self, portIndex):
        return self._number

    def setInData(self, nodeData, portIndex):
        pass

    def embeddedWidget(self):
        return self._lineEdit

    def onTextEdited(self, txt):
        number, ok = self._lineEdit.text().toDouble()
        if ok:
            self._number = DecimalData(number)
            self.emit.dataUpdated(0)
        else:
            self._number = None
            self.emit.dataInvalidated(0)
