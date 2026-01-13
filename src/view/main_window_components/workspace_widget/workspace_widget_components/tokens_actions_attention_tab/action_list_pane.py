from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.config import settings

import html

class ActionListPane(QWidget):
    action_clicked = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(250)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("<b>Actions List</b>"))
        
        self.list_widget = QListWidget()
        stylesheet = settings.get_stylesheets("QList_style.qss","QScrollBar_style.qss")
        self.list_widget.setStyleSheet(stylesheet)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        
        layout.addWidget(self.list_widget)

    def populate(self, actions_list):
        self.list_widget.clear()
        for i,action in enumerate(actions_list):
            item = QListWidgetItem()
            raw_text = f"{action}"
            item.setData(Qt.ItemDataRole.UserRole, raw_text)
            safe_text = html.escape(raw_text)
            testo_html = f"<span style='color: white;'>{i}){safe_text}</span>"
            
            label = QLabel(testo_html)
            label.setStyleSheet("background-color: transparent;")
            label.setContentsMargins(5, 2, 5, 2)
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, label)
            item.setSizeHint(label.sizeHint())

    def _on_item_clicked(self, item):
        row = self.list_widget.row(item)
        text = item.data(Qt.ItemDataRole.UserRole)
        self.action_clicked.emit(row, text)

    def get_current_selection(self):
        return self.list_widget.currentItem()

    def highlight_actions(self, top_indices, action_selected, gt_indices=None, show_gt=False):
        """
        Evidenzia azioni con logica 3 colori se show_gt è True:
        """
        # Palette Colori
        COLOR_MATCH = settings.GRAPH_PALETTE["EXPLICIT_LINK_FOUND"]
        COLOR_MODEL_ONLY =settings.GRAPH_PALETTE["ACTIONS_CORRELATED"]
        COLOR_GT_ONLY = settings.GRAPH_PALETTE["EXPLICIT_LINK_NOT_FOUND"]
        COLOR_TRANSPARENT = "transparent"
        COLOR_BORDER_SEL = settings.GRAPH_PALETTE["ACTION_SOURCE"]

        if gt_indices is None:
            gt_indices = set()

        # Convertiamo top_indices in set per efficienza
        top_indices_set = set(top_indices)
        
        self.list_widget.clearSelection()
        
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            label_widget = self.list_widget.itemWidget(item)
            
            if not label_widget: continue

            # --- LOGICA COLORE SFONDO ---
            bg_color = COLOR_TRANSPARENT
            
            if show_gt:
                is_in_pred = row in top_indices_set
                is_in_gt = row in gt_indices
                
                if is_in_pred and is_in_gt:
                    bg_color = COLOR_MATCH
                elif is_in_pred and not is_in_gt:
                    bg_color = COLOR_MODEL_ONLY
                elif not is_in_pred and is_in_gt:
                    bg_color = COLOR_GT_ONLY
            else:
                if row in top_indices_set:
                    bg_color = settings.GRAPH_PALETTE["ACTIONS_CORRELATED"]

            # --- LOGICA BORDO ---
            is_selected = (row == action_selected)
            border_style = f"border-bottom: 2px solid {COLOR_BORDER_SEL};" if is_selected else "border: none;"
            
            # --- APPLICAZIONE STILE ---
            style_rules = [
                "border-radius: 4px;",
                f"background-color: {bg_color};",
                border_style
            ]
            
            label_widget.setStyleSheet(" ".join(style_rules))
            item.setBackground(QColor("transparent"))

    def highlight_tokens_in_text(self, highlights_per_action, section_of_action_selected):
        current_selected_row = self.list_widget.currentRow()
        c_text_normal = "white"
        c_text_highlight = settings.GRAPH_PALETTE["TOKEN_CORRELATED"]
        c_text_selected = settings.GRAPH_PALETTE["TOKEN_SOURCE"]
        
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            label_widget = self.list_widget.itemWidget(item)
            if not label_widget: continue
                
            raw_text = item.data(Qt.ItemDataRole.UserRole)
            sections = raw_text.split("_")
            row_highlights = highlights_per_action.get(row, set())
            new_html_parts = []
            common_style="font-weight: bold; border-radius: 2px;"
            
            for i, section in enumerate(sections):
                safe_section = html.escape(section)
                is_in_highlight_list = (i in row_highlights)
                is_current_selection = (row == current_selected_row and i == section_of_action_selected)
                
                if is_current_selection and is_in_highlight_list:
                    style = f"color: {c_text_selected}; background-color: {c_text_highlight};{common_style}"
                elif is_current_selection:
                    style = f"color: {c_text_selected}; {common_style}"
                elif is_in_highlight_list:
                    style = f"color: {c_text_normal}; background-color: {c_text_highlight}; {common_style}"
                else:
                    style = f"color: {c_text_normal};"
                
                new_html_parts.append(f"<span style='{style}'>{safe_section}</span>")
            
            label_widget.setText(f"{row})"+"_".join(new_html_parts))