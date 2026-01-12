import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsPathItem, QGraphicsTextItem
from PyQt6.QtGui import QColor, QFont, QPainterPath, QFontMetrics, QPainter
from PyQt6.QtCore import QRectF, QPointF

from src.config import settings

from .graph_utils import BaseNodeItem, draw_vertical_squared_link
from .token_attention_workboard import ZoomableGraphicsView

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

        font_node = QFont(settings.TEXT_FONT, settings.TEXT_SIZE)
        fm = QFontMetrics(font_node)
        padding_node = 24
        gap = 30

        target_nodes_data = []
        total_block_width = 0

        for t_idx in top_indices:
            weight = row_data[t_idx]
            text = f"{t_idx}) {all_actions[t_idx]}"
            
            # Calcola la larghezza esatta che avrà il nodo
            node_width = fm.horizontalAdvance(text) + padding_node
            
            target_nodes_data.append({
                'idx': t_idx,
                'text': text,
                'weight': weight,
                'width': node_width
            })
            
            total_block_width += node_width

        if len(target_nodes_data) > 1:
            total_block_width += (len(target_nodes_data) - 1) * gap

        # Nodo Source (Posizionato in basso al centro 0,0)
        src_rect = self._add_node(0, 0, source_name, QColor(settings.GRAPH_PALETTE["ACTION_SOURCE"]), source_idx)
        src_out = QPointF(src_rect.center().x(), src_rect.top())
        
        target_y = -150
        font_link = QFont(settings.TEXT_FONT, settings.TEXT_SIZE)

        # Calcoliamo il punto X sinistro da cui iniziare a disegnare per essere centrati
        current_left_x = -(total_block_width / 2)

        #disegno gli elementi correlati
        for item in target_nodes_data:
            node_center_x = current_left_x + (item['width'] / 2)
            
            # Disegna nodo
            dst_rect = self._add_node(node_center_x, target_y, item['text'], 
                                      QColor(settings.GRAPH_PALETTE["ACTIONS_CORRELATED"]), item['idx'])
            
            # Disegna link
            dst_in = QPointF(dst_rect.center().x(), dst_rect.bottom())
            draw_vertical_squared_link(self.scene, src_out, dst_in, item['weight'], font_link)
            
            # Avanza il cursore X: Larghezza nodo appena fatto + Gap
            current_left_x += item['width'] + gap
            
        self.view.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50,-50,50,50))
        return top_indices

    def _add_node(self, x, y, text, color, idx):
        font = QFont("Arial", 10)
        fm = QFontMetrics(font)
        w = fm.horizontalAdvance(text) + 24
        h = fm.height() + 20
        rect = QRectF(x - w/2, y - h/2, w, h)
        
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        node = BaseNodeItem(path, rect, text, 
                            QColor(color.red(), color.green(), color.blue(), 100), 
                            color, font, idx)
        self.scene.addItem(node)
        return rect