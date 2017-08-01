import math
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPen, QLinearGradient, QFontMetrics

from NodeDataModel import NodeDataModel, NodeValidationState, ConnectionPolicy
from PortType import PortType
from StyleCollection import StyleCollection


class NodePainter:
    @staticmethod
    def drawNodeRect(painter, geom, model, graphicsObject):
        nodeStyle = model.nodeStyle()

        color = nodeStyle.SelectedBoundaryColor if graphicsObject.isSelected() else nodeStyle.NormalBoundaryColor

        if geom.hovered():
            p = QPen(color, nodeStyle.HoveredPenWidth)
            painter.setPen(p)
        else:
            p = QPen(color, nodeStyle.PenWidth)
            painter.setPen(p)

        gradient = QLinearGradient(QPointF(0.0, 0.0),
                                   QPointF(2.0, geom.height()))

        gradient.setColorAt(0.0, nodeStyle.GradientColor0)
        gradient.setColorAt(0.03, nodeStyle.GradientColor1)
        gradient.setColorAt(0.97, nodeStyle.GradientColor2)
        gradient.setColorAt(1.0, nodeStyle.GradientColor3)

        painter.setBrush(gradient)

        diam = nodeStyle.ConnectionPointDiameter
        boundary = QRectF( -diam, -diam, 2.0 * diam + geom.width(), 2.0 * diam + geom.height())
        radius = 3.0
        painter.drawRoundedRect(boundary, radius, radius)

    @staticmethod
    def drawDragRect(painter, geom, model):
        nodeStyle = model.nodeStyle()
        color = nodeStyle.SelectedBoundaryColor

        p = QPen(color, nodeStyle.PenWidth)
        painter.setPen(p)
        gradient = QLinearGradient(QPointF(0.0, 0.0),
                                   QPointF(2.0, geom.height()))
        gradient.setColorAt(0.0, nodeStyle.GradientColor0)
        gradient.setColorAt(0.03, nodeStyle.GradientColor1)
        gradient.setColorAt(0.97, nodeStyle.GradientColor2)
        gradient.setColorAt(1.0, nodeStyle.GradientColor3)
        painter.setBrush(gradient)

        diam = nodeStyle.ConnectionPointDiameter
        boundary = QRectF( 0.0, 0.0, 2.0 * diam + geom.width(), 2.0 * diam + geom.height())
        radius = 3.0
        painter.drawRoundedRect(boundary, radius, radius)

        name = model.caption()
        f = painter.font()
        f.setBold(True)
        metrics = QFontMetrics(f)

        rect = metrics.boundingRect(name)
        position = QPointF(diam + (geom.width() - rect.width()) / 2.0,
                           diam + (geom.spacing() + geom.entryHeight()) / 3.0)

        painter.setFont(f)
        painter.setPen(nodeStyle.FontColor)
        painter.drawText(position, name)

        f.setBold(False)
        painter.setFont(f)

    @staticmethod
    def drawConnectionPoints(painter, geom, state, model, scene):
        nodeStyle = StyleCollection().nodeStyle()
        diameter = nodeStyle.ConnectionPointDiameter
        reducedDiameter = diameter * 0.6

        portTypes = [PortType.Out, PortType.In]
        for portType in portTypes:
            for i in range(0, len(state.getEntries(portType))):
                p = geom.portScenePosition(i, portType)
                dataType = model.dataType(portType, i)
                canConnect = (len(state.getEntries(portType)[i]) == 0
                              or (portType == PortType.Out and
                                  model.portOutConnectionPolicy(i) == ConnectionPolicy.Many))
                r = 1.0
                if state.isReacting() and canConnect and portType == state.reactingPortType():
                    diff = geom.draggingPos() - p
                    dist = math.sqrt(QPointF.dotProduct(diff, diff))
                    typeConvertable = False
                    if portType == PortType.In:
                        typeConvertable = scene.registry().getTypeConverter(state.reactingDataType().id, dataType.id) != None
                    else:
                        typeConvertable = scene.registry().getTypeConverter(dataType.id, state.reactingDataType().id) != None
                    if state.reactingDataType().id == dataType.id or typeConvertable:
                        thres = 40.0
                        r = (2.0 - dist / thres) if dist < thres else 1.0
                    else:
                        thres = 80.0
                        r = (dist / thres) if dist < thres else 1.0

                painter.setBrush(nodeStyle.ConnectionPointColor)
                painter.drawEllipse(p, reducedDiameter * r, reducedDiameter * r)

    @staticmethod
    def drawFilledConnectionPoints(painter, geom, state, model):
        nodeStyle = StyleCollection().nodeStyle()
        diameter = nodeStyle.ConnectionPointDiameter

        portTypes = [PortType.Out, PortType.In]
        for portType in portTypes:
            for i in range(0, len(state.getEntries(portType))):
                p = geom.portScenePosition(i, portType)
                if len(state.getEntries(portType)[i]) != 0:
                    dataType = model.dataType(portType, i)
                    painter.setPen(nodeStyle.FilledConnectionPointColor)
                    painter.setBrush(nodeStyle.FilledConnectionPointColor)
                    painter.drawEllipse(p, diameter * 0.4, diameter * 0.4)

    @staticmethod
    def drawModelName(painter, geom, state, model):
        if not model.captionVisible():
            return

        nodeStyle = StyleCollection().nodeStyle()
        name = model.caption()
        f = painter.font()
        f.setBold(True)
        metrics = QFontMetrics(f)

        rect = metrics.boundingRect(name)
        position = QPointF((geom.width() - rect.width()) / 2.0,
                           (geom.spacing() + geom.entryHeight()) / 3.0)

        painter.setFont(f)
        painter.setPen(nodeStyle.FontColor)
        painter.drawText(position, name)

        f.setBold(False)
        painter.setFont(f)

    @staticmethod
    def drawEntryLabels(painter, geom, state, model):
        metrics = painter.fontMetrics()
        nodeStyle = StyleCollection().nodeStyle()

        portTypes = [PortType.Out, PortType.In]
        for portType in portTypes:
            entries = state.getEntries(portType)
            for i in range(0, len(entries)):
                p = geom.portScenePosition(i, portType)
                if len(entries[i]) == 0:
                    painter.setPen(nodeStyle.FontColorFaded)
                else:
                    painter.setPen(nodeStyle.FontColor)
                s = model.dataType(portType, i).name if model.portCaptionVisible(portType, i) else model.dataType(portType, i).name
                rect = metrics.boundingRect(s)
                p.setY(p.y() + rect.height() / 4.0)
                if portType == PortType.In:
                    p.setX(5.0)
                elif portType == PortType.Out:
                    p.setX(geom.width() - 5.0 - rect.width())
                painter.drawText(p, s)

    @staticmethod
    def drawResizeRect(painter, geom, model):
        if model.resizable():
            painter.setBrush(Qt.gray)
            painter.drawEllipse(geom.resizeRect())

    @staticmethod
    def drawValidationRect(painter, geom, model, graphicsObject):
        modelValidationState = model.validationState()
        if modelValidationState != NodeValidationState.Valid:
            nodeStyle = StyleCollection().nodeStyle()
            color = nodeStyle.SelectedBoundaryColor if graphicsObject.isSelected() else nodeStyle.NormalBoundaryColor
            if geom.hovered():
                p = QPen(color, nodeStyle.HoveredPenWidth)
                painter.setPen(p)
            else:
                p = QPen(color, nodeStyle.PenWidth)
                painter.setPen(p)
            if modelValidationState == NodeValidationState.Error:
                painter.setBrush(nodeStyle.ErrorColor)
            else:
                painter.setBrush(nodeStyle.WarningColor)
            radius = 3.0
            diam = nodeStyle.ConnectionPointDiameter
            boundary = QRectF(-diam, -diam + geom.height() - geom.validationHeight(),
                              2.0 * diam + geom.width(), 2.0 * diam + geom.validationHeight())
            painter.drawRoundedRect(boundary, radius, radius)

            painter.setBrush(Qt.gray)
            errorMsg = model.validationMessage()
            f = painter.font()
            metrics = QFontMetrics(f)
            rect = metrics.boundingRect(errorMsg)
            position = QPointF((geom.width() - rect.width()) / 2.0,
                               geom.height() - (geom.validationHeight() - diam) / 2.0)
            painter.setFont(f)
            painter.setPen(nodeStyle.FontColor)
            painter.drawText(position, errorMsg)

    @staticmethod
    def paint(painter, node, scene):
        geom = node.nodeGeometry()
        state = node.nodeState()
        graphicsObject = node.nodeGraphicsObject()
        geom.recalculateSizeForFont(painter.font())
        model = node.nodeDataModel()

        NodePainter.drawNodeRect(painter, geom, model, graphicsObject)
        NodePainter.drawConnectionPoints(painter, geom, state, model, scene)
        NodePainter.drawFilledConnectionPoints(painter, geom, state, model)
        NodePainter.drawModelName(painter, geom, state, model)
        NodePainter.drawEntryLabels(painter, geom, state, model)
        NodePainter.drawResizeRect(painter, geom, model)
        NodePainter.drawValidationRect(painter, geom, model, graphicsObject)

        # call custom painter
        # painterDelegate = model.painterDelegate()
        # if painterDelegate:
        #     painterDelegate.paint(painter, geom, model)
