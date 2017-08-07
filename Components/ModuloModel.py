from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgWidget

from Components.IntegerData import IntegerData
from NodeDataModel import NodeDataModel, NodeValidationState
from PortType import PortType

import modeller_rcc

class ModuloModel(NodeDataModel):
    def __init__(self):
        super(ModuloModel, self).__init__()
        self._number1 = None
        self._number2 = None
        self._result = None
        self.modelValidationState = NodeValidationState.Warning
        self.modelValidationError = "Missing or incorrect inputs"
        self._svgWidget = QSvgWidget(":/Components/images/mod.svg")
        defaultSize = QSize(36, 36)
        self._svgWidget.resize(defaultSize)
        self._svgWidget.setAttribute( Qt.WA_TranslucentBackground)
        self._svgWidget.setMinimumSize(defaultSize)

    def clone(self):
        return ModuloModel()

    def name(self):
        return "Modulo"

    def caption(self):
        return "Modulo"

    def captionVisible(self):
        return  True

    def portCaption(self, portType, portIndex):
        if portType == PortType.Out:
            return "Result"
        return "Dividend" if portIndex == 0 else "Divisor"

    def portCaptionVisible(self, portType, portIndex):
        return True

    def nPorts(self, portType):
        return 2 if portType == PortType.In else 1

    def dataType(self, portType, portIndex):
        return IntegerData().type()

    def outData(self, portIndex):
        return self._result

    def setInData(self, nodeData, portIndex):
        if portIndex == 0:
            self._number1 = nodeData
        else:
            self._number2 = nodeData

        if self._number1 is None or self._number2 is None:
            self.modelValidationError = "Missing or incorrect inputs"
            self.modelValidationState = NodeValidationState.Warning
            self._result = None
            return

        if self._number2.number() == 0:
            self.modelValidationError = "Division by zero error"
            self.modelValidationState = NodeValidationState.Error
            self._result = None
            return

        self.modelValidationState = NodeValidationState.Valid
        self.modelValidationError = ""
        self._result = IntegerData(self._number1.number() / self._number2.number())

        self.emit.dataUpdated(0)

    def embeddedWidget(self):
        return self._svgWidget

    def validationState(self):
        return self.modelValidationState

    def validationMessage(self):
        return self.modelValidationError

