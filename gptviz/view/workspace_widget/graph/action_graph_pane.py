import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene
from PyQt6.QtGui import QColor, QFont, QPainterPath, QFontMetrics, QPainter, QPen
from PyQt6.QtCore import QRectF, QPointF, Qt

from ....config import settings
from ..graph.graph_utils import BaseNodeItem, draw_vertical_squared_link
from ..graph.token_attention_workboard import ZoomableGraphicsView

class ActionGraphPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        layout.addWidget(self.view)

    def draw_graph(self, source_idx, source_name, agg_matrix, all_actions, top_k, action_link_matrices):
        self.scene.clear()
        
        row_data = agg_matrix[source_idx]
        sorted_idx = np.argsort(row_data)[::-1]
        pred_indices_set = set([i for i in sorted_idx if row_data[i] > 0.001][:top_k])
        
        gt_indices_set = set()
        
        if action_link_matrices is not None:
            gt_matrix = action_link_matrices[0] if isinstance(action_link_matrices, list) else action_link_matrices
            
            if gt_matrix is not None:
                try:
                    gt_row = gt_matrix[source_idx]
                    gt_indices_set = set(np.where(gt_row == 1)[0])
                except IndexError:
                    print(f"Warning: Source index {source_idx} out of bounds for GT matrix.")

        all_target_indices = list(pred_indices_set.union(gt_indices_set))
        all_target_indices.sort(key=lambda x: row_data[x], reverse=True)

        font_node = QFont(settings.TEXT_FONT, settings.TEXT_SIZE)
        fm = QFontMetrics(font_node)
        padding_node = 24
        gap = 30

        target_nodes_data = []
        total_block_width = 0

        # Colori per i tre stati
        COLOR_MATCH = QColor(settings.GRAPH_PALETTE["EXPLICIT_LINK_FOUND"])
        COLOR_MODEL_ONLY = QColor(settings.GRAPH_PALETTE["ACTIONS_CORRELATED"])
        COLOR_GT_ONLY =  QColor(settings.GRAPH_PALETTE["EXPLICIT_LINK_NOT_FOUND"])

        for t_idx in all_target_indices:
            weight = row_data[t_idx]
            text = f"{t_idx}) {all_actions[t_idx]}"
            
            is_in_pred = t_idx in pred_indices_set
            is_in_gt = t_idx in gt_indices_set
            
            node_color = QColor("#95a5a6")
            border_style = Qt.PenStyle.SolidLine
            
            if is_in_pred and is_in_gt:
                node_color = COLOR_MATCH
                status = "MATCH"
            elif is_in_pred and not is_in_gt:
                node_color = COLOR_MODEL_ONLY
                status = "PRED_ONLY"
            elif not is_in_pred and is_in_gt:
                node_color = COLOR_GT_ONLY
                status = "GT_ONLY"
                border_style = Qt.PenStyle.DashLine
                text += " (Miss)"
                if weight < 0.001: weight = 0.001

            node_width = fm.horizontalAdvance(text) + padding_node
            
            target_nodes_data.append({
                'idx': t_idx,
                'text': text,
                'weight': weight,
                'width': node_width,
                'color': node_color,
                'status': status,
                'border': border_style
            })
            
            total_block_width += node_width

        if len(target_nodes_data) > 1:
            total_block_width += (len(target_nodes_data) - 1) * gap

        # --- Disegno ---

        # Nodo Source
        src_rect = self._add_node(0, 0, source_name, QColor(settings.GRAPH_PALETTE["ACTION_SOURCE"]), source_idx)
        src_out = QPointF(src_rect.center().x(), src_rect.top())
        
        target_y = -150
        font_link = QFont(settings.TEXT_FONT, settings.TEXT_SIZE)

        current_left_x = -(total_block_width / 2)

        for item in target_nodes_data:
            node_center_x = current_left_x + (item['width'] / 2)
            
            # Disegna nodo target con il colore specifico calcolato prima
            dst_rect = self._add_node(
                node_center_x, 
                target_y, 
                item['text'], 
                item['color'], 
                item['idx'],
                border_style=item['border'] # Passiamo lo stile del bordo
            )
            
            dst_in = QPointF(dst_rect.center().x(), dst_rect.bottom())            
            draw_vertical_squared_link(self.scene, src_out, dst_in, font_link,( item['weight'] if item['status'] != "GT_ONLY" else None) )
            
            current_left_x += item['width'] + gap
            
        self.view.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50,-50,50,50))
        
        # Ritorna gli indici predetti originali per compatibilità
        return list(pred_indices_set)

    def _add_node(self, x, y, text, color, idx, border_style=Qt.PenStyle.SolidLine):
        font = QFont("Arial", 10)
        fm = QFontMetrics(font)
        w = fm.horizontalAdvance(text) + 24
        h = fm.height() + 20
        rect = QRectF(x - w/2, y - h/2, w, h)
        
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        # Colore sfondo semi-trasparente
        bg_color = QColor(color.red(), color.green(), color.blue(), 40)
        border_color = color
        
        node = BaseNodeItem(path, rect, text, bg_color, border_color, font, idx)
        
        pen = node.pen()
        pen.setStyle(border_style)
        if border_style == Qt.PenStyle.DashLine:
            pen.setWidth(2)
        node.setPen(pen)

        self.scene.addItem(node)
        return rect