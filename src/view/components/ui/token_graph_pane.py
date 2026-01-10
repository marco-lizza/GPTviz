import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QGraphicsScene, QGraphicsPathItem)
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QFontMetrics,QIcon
from PyQt6.QtCore import QRectF, QPointF

from src.config import settings

from .graph_utils import BaseNodeItem, draw_squared_link
from .token_attention_workboard import ZoomableGraphicsView

class TokenGraphPane(QWidget):
    """Pannello inferiore: dettaglio Token."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # --- Toolbar ---
        tool_layout = QHBoxLayout()
        tool_layout.setContentsMargins(5, 5, 5, 0)

        self.focus_token_label = QLabel("Focus Token:")
        self.focus_token_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        
        tool_layout.addWidget(self.focus_token_label)
        self.token_selector = QComboBox()
        self.token_selector.setStyleSheet(settings.get_stylesheet("QComboBox_style.qss"))
        self.token_selector.currentIndexChanged.connect(self.on_token_selected)
        tool_layout.addWidget(self.token_selector, 1)
        
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        tool_layout.addWidget(self.lbl_info)
        layout.addLayout(tool_layout)

        # --- Grafica ---
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        layout.addWidget(self.view)
        
        # Dati interni
        self.global_matrix = None
        self.global_tokens = []
        self.top_k = 5
        self.current_top_targets = [] # Per evidenziare nella lista principale

    def load_action_tokens(self, action_name, global_matrix, all_tokens, action_indices, top_k):
        self.global_matrix = global_matrix
        self.global_tokens = all_tokens
        self.top_k = top_k
        
        self.token_selector.blockSignals(True)
        self.token_selector.clear()
        
        if not action_indices:
            self.lbl_info.setText("No tokens mapping")
            self.scene.clear()
            self.token_selector.blockSignals(False)
            return

        for idx in action_indices:
            token_word = all_tokens[idx]
            icon_path = "assets/utility/token.svg" 
            icon = QIcon(icon_path)
            self.token_selector.addItem(icon,f"{token_word}", idx)
            
        self.token_selector.blockSignals(False)
        
        if self.token_selector.count() > 0:
            self.token_selector.setCurrentIndex(0)
            self.on_token_selected(0)

    def on_token_selected(self, index):
        if index < 0: return
        global_idx = self.token_selector.itemData(index)
        token_word = self.token_selector.currentText()
        self.draw_global_token_graph(global_idx)

    def draw_global_token_graph(self, source_idx):
        self.scene.clear()
        if self.global_matrix is None: return

        attention_row = self.global_matrix[source_idx]
        sorted_indices = np.argsort(attention_row)[::-1]
        
        self.current_top_targets = []
        for idx in sorted_indices:
            if len(self.current_top_targets) >= self.top_k: break
            if attention_row[idx] < 0.001: continue
            self.current_top_targets.append(idx)
            
        source_name = self.global_tokens[source_idx]
        
        # Source Node
        src_rect = self._add_node(0, 0, source_name, QColor("#E54DBA"), source_idx)
        src_out = QPointF(src_rect.right(), src_rect.center().y())

        # Target Nodes
        start_x = 300
        spacing_y = 60
        total_h = len(self.current_top_targets) * spacing_y
        current_y = -(total_h / 2) + (spacing_y / 2)
        font_link = QFont("Arial", 7)
        
        for t_idx in self.current_top_targets:
            weight = attention_row[t_idx]
            target_name = self.global_tokens[t_idx]
            
            dst_rect = self._add_node(start_x, current_y, target_name, QColor("#61afef"), t_idx)
            dst_in = QPointF(dst_rect.left(), dst_rect.center().y())
            
            draw_squared_link(self.scene, src_out, dst_in, weight, font_link)
            current_y += spacing_y

        self.view.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))
        self.lbl_info.setText(f"Top-{self.top_k} connections for '{source_name}'")

    def _add_node(self, x, y, text, color, idx):
        font = QFont("Arial", 11)
        fm = QFontMetrics(font)
        w = fm.horizontalAdvance(text) + 20
        h = 30
        rect = QRectF(x, y - h/2, w, h)
        path = QPainterPath()
        path.addRoundedRect(rect, 4, 4)
        
        node = BaseNodeItem(path, rect, text, 
                            QColor(color.red(), color.green(), color.blue(), 150), 
                            color, font, idx)
        self.scene.addItem(node)
        return rect