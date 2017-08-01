from Components.DecimalData import DecimalData
from Components.IntegerData import IntegerData
from NodeDataModel import NodeDataModel, NodeValidationState
from PortType import PortType


class IntegerToDecimalConverterDataModel(NodeDataModel):
    def __init__(self):
        super(IntegerToDecimalConverterDataModel, self).__init__()
        self._in = None
        self._out = None
        self.modelValidationState = NodeValidationState.Warning
        self.modelValidationError = "Missing or incorrect inputs"

    def clone(self):
        return IntegerToDecimalConverterDataModel()

    def name(self):
        return "IntegerToDecimalConverter"

    def caption(self):
        return "Integer To Decimal"

    def captionVisible(self):
        return True

    def portCaptionVisible(self, portType, portIndex):
        return False

    def portCaption(self, portType, portIndex):
        return ""

    def nPorts(self, portType):
        return 1

    def dataType(self, portType, portIndex):
        return IntegerData().type() if portType == PortType.In else DecimalData().type()

    def outData(self, portIndex):
        return self._out

    def setInData(self, nodeData, portIndex):
        self._in = nodeData

        if self._in is None:
            self.modelValidationError = "Missing or incorrect inputs"
            self.modelValidationState = NodeValidationState.Warning
            self._out = None
            return

        self.modelValidationState = NodeValidationState.Valid
        self.modelValidationError = ""
        self._out = DecimalData(float(self._in.number()))

        self.emit.dataUpdated(0)

    def embeddedWidget(self):
        return None

    def validationState(self):
        return self.modelValidationState

    def validationMessage(self):
        return self.modelValidationError
