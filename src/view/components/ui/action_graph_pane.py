import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsPathItem, QGraphicsTextItem
from PyQt6.QtGui import QColor, QFont, QPainterPath, QFontMetrics, QPainter
from PyQt6.QtCore import QRectF, QPointF

from src.config import settings

# Importa BaseNodeItem e draw_squared_link dal file utils
from .graph_utils import BaseNodeItem, draw_squared_link
from .token_attention_workboard import ZoomableGraphicsView  # Mantengo import originale

class ActionGraphPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        layout.addWidget(self.view)

    def draw_graph(self, source_idx, source_name, agg_matrix, all_actions, top_k):
        self.scene.clear()
        
        row_data = agg_matrix[source_idx]
        sorted_idx = np.argsort(row_data)[::-1]
        top_indices = [i for i in sorted_idx if row_data[i] > 0.001][:top_k]

        # Nodo Source
        src_rect = self._add_node(0, 0, source_name, QColor("#F4D35E"), source_idx)
        src_out = QPointF(src_rect.right(), src_rect.center().y())
        
        # Nodi Target
        spacing_y = 80
        curr_y = -((len(top_indices)*spacing_y)/2) + (spacing_y/2)
        font_link = QFont("Arial", 7)

        for t_idx in top_indices:
            weight = row_data[t_idx]
            t_name = f"{t_idx}) "+all_actions[t_idx]
            
            dst_rect = self._add_node(350, curr_y, t_name, QColor(settings.PALETTE["app_color"]), t_idx)
            dst_in = QPointF(dst_rect.left(), dst_rect.center().y())
            
            draw_squared_link(self.scene, src_out, dst_in, weight, font_link)
            curr_y += spacing_y
            
        self.view.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50,-50,50,50))
        return top_indices

    def _add_node(self, x, y, text, color, idx):
        font = QFont("Arial", 10)
        fm = QFontMetrics(font)
        w = fm.horizontalAdvance(text) + 24
        h = fm.height() + 20
        rect = QRectF(x, y - h/2, w, h)
        
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        node = BaseNodeItem(path, rect, text, 
                            QColor(color.red(), color.green(), color.blue(), 100), 
                            color, font, idx)
        self.scene.addItem(node)
        return rect