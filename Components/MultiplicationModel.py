from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgWidget

from Components.DecimalData import DecimalData
from NodeDataModel import NodeDataModel, NodeValidationState
from PortType import PortType

import modeller_rcc

class MultiplicationModel(NodeDataModel):
    def __init__(self):
        super(MultiplicationModel, self).__init__()
        self._numbers = [None, None]
        self._result = None
        self.modelValidationState = NodeValidationState.Warning
        self.modelValidationError = "Missing or incorrect inputs"
        self._svgWidget = QSvgWidget(":/Components/images/mul.svg")
        defaultSize = QSize(36, 36)
        self._svgWidget.resize(defaultSize)
        self._svgWidget.setAttribute( Qt.WA_TranslucentBackground)
        self._svgWidget.setMinimumSize(defaultSize)

    def clone(self):
        return MultiplicationModel()

    def name(self):
        return "Multiplication"

    def caption(self):
        return "Multiplication"

    def captionVisible(self):
        return True

    def portCaption(self, portType, portIndex):
        return "Result" if portType == PortType.Out else "Multiplier"

    def portCaptionVisible(self, portType, portIndex):
        return True

    def nPorts(self, portType):
        return 2 if portType == PortType.In else 1

    def dataType(self, portType, portIndex):
        return DecimalData().type()

    def outData(self, portIndex):
        return self._result

    def setInData(self, nodeData, portIndex):
        self._numbers[portIndex] = nodeData

        if self._numbers[0] is None or self._numbers[1] is None:
            self.modelValidationError = "Missing or incorrect inputs"
            self.modelValidationState = NodeValidationState.Warning
            self._result = None
            return

        self.modelValidationState = NodeValidationState.Valid
        self.modelValidationError = ""
        self._result = DecimalData(self._number[0].number() * self._number[1].number())

        self.emit.dataUpdated(0)

    def embeddedWidget(self):
        return self._svgWidget

    def validationState(self):
        return self.modelValidationState

    def validationMessage(self):
        return self.modelValidationError

