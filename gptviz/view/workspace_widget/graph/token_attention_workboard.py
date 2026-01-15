from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui import (QPen, QColor, QPainter)

from ....config import settings

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.bg_color = QColor("#2b2b2b")
        self.grid_color = QColor("#3a3a3a")
        self.grid_size = 30
        self.setStyleSheet("border: 0px;")

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, self.bg_color)
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        x = left
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += self.grid_size
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += self.grid_size

    def wheelEvent(self, event):
        super().wheelEvent(event)
        zoom_factor = settings.ZOOM_FACTOR if hasattr(settings, 'ZOOM_FACTOR') else 1.05
        min_zoom = settings.MIN_ZOOM if hasattr(settings, 'MIN_ZOOM') else 0.5
        max_zoom = settings.MAX_ZOOM if hasattr(settings, 'MAX_ZOOM') else 1.5

        if event.angleDelta().y() > 0:
            factor = zoom_factor
        else:
            factor = 1 / zoom_factor
        current_scale = self.transform().m11()
        future_scale = current_scale * factor
        if min_zoom <= future_scale <= max_zoom:
            self.scale(factor, factor)
