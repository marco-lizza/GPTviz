import numpy as np
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath

class BaseNodeItem(QGraphicsPathItem):
    """Nodo grafico generico (usato sia per Azioni che per Token)."""
    def __init__(self, path, rect, text, fill_color, border_color, font, data_idx=None):
        super().__init__(path)
        self.setBrush(QBrush(fill_color))
        self.setPen(QPen(border_color, 2.0))
        self.setZValue(10)
        self.setAcceptHoverEvents(True)
        self.data_idx = data_idx
        
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor("#FFFFFF"))
        txt_rect = self.text_item.boundingRect()
        self.text_item.setPos(rect.center().x() - txt_rect.width()/2, 
                              rect.center().y() - txt_rect.height()/2)

def draw_squared_link(scene, p1: QPointF, p2: QPointF, weight: float, font):
    """Disegna una linea squadrata (Orizzontale -> Verticale -> Orizzontale) sulla scena."""
    path = QPainterPath()
    path.moveTo(p1)
    
    mid_x = (p1.x() + p2.x()) / 2
    path.lineTo(mid_x, p1.y())
    path.lineTo(mid_x, p2.y())
    path.lineTo(p2.x(), p2.y())
    
    item = QGraphicsPathItem(path)
    # Spessore dinamico
    width = 1.0 + (weight * 5.0)
    # Colore grigio scuro dinamico
    color_val = int(min(255, 100 + weight * 155))
    color = QColor(80, 80, 80, color_val)
    
    pen = QPen(color, width)
    pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin) # Angoli netti
    item.setPen(pen)
    item.setZValue(-1)
    scene.addItem(item)
    
    # Label peso
    txt = QGraphicsTextItem(f"{weight:.3f}")
    txt.setFont(font)
    br = txt.boundingRect()
    # Posiziona vicino al target
    txt.setPos(p2.x() - br.width() - 5, p2.y() - br.height() - 2)
    scene.addItem(txt)