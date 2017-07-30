from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainterPath, QPainterPathStroker, QPen

from StyleCollection import StyleCollection


class ConnectionPainter:
    @staticmethod
    def cubicPath(geom):
        source = geom.source()
        sink = geom.sink()
        c1c2 = geom.pointsC1C2()
        cubic = QPainterPath(source)
        cubic.cubicTo(c1c2[0], c1c2[1], sink)
        return cubic

    @staticmethod
    def getPainterStroke(geom):
        cubic = ConnectionPainter.cubicPath(geom)
        source = geom.source()
        result = QPainterPath(source)
        segments = 20
        for i in range(0, segments):
            ratio = float(i + 1) / segments
            result.lineTo(cubic.pointAtPercent(ratio))
        stroker = QPainterPathStroker()
        stroker.setWidth(10.0)
        return stroker.createStroke(result)

    @staticmethod
    def paint(painter, connection):
        connectionStyle = StyleCollection().connectionStyle()
        normalColor   = connectionStyle.NormalColor
        hoverColor    = connectionStyle.HoveredColor
        selectedColor = connectionStyle.SelectedColor
        dataType = connection.dataType()

        geom = connection.connectionGeometry()
        state = connection.connectionState()

        lineWidth = connectionStyle.LineWidth
        pointDiameter = connectionStyle.PointDiameter

        cubic = ConnectionPainter.cubicPath(geom)
        hovered = geom.hovered()
        graphicsObject = connection.getConnectionGraphicsObject()
        selected = graphicsObject.isSelected()

        if hovered or selected:
            p = QPen()
            p.setWidth(2 * lineWidth)
            c = connectionStyle.SelectedHaloColor if selected else hoverColor
            p.setColor(c)
            painter.setPen(p)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(cubic)
        else:
            p = QPen()
            p.setWidth(lineWidth)
            c = selectedColor if selected else normalColor
            p.setColor(c)
            if state.requiresPort():
                p.setWidth(connectionStyle.ConstructionLineWidth)
                p.setColor(connectionStyle.ConstructionColor)
                p.setStyle(Qt.DashLine)
            painter.setPen(p)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(cubic)

        source = geom.source()
        sink = geom.sink()
        painter.setPen(connectionStyle.ConstructionColor)
        painter.setBrush(connectionStyle.ConstructionColor)
        pointRadius = pointDiameter / 2.0
        painter.drawEllipse(source, pointRadius, pointRadius)
        painter.drawEllipse(sink, pointRadius, pointRadius)




