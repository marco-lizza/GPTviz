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
            
            # Importante: Salva il testo "puro" nei dati, così la logica non si rompe
            item.setData(Qt.ItemDataRole.UserRole, raw_text)
            
            # QUI FAI L'ESCAPE: converte "<token>" in "&lt;token&gt;"
            safe_text = html.escape(raw_text)
            
            # Ora safe_text può essere inserito nell'HTML senza essere interpretato come tag
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

    def highlight_actions(self, top_indices, action_selected):
        """
        Evidenzia le azioni Top-K (sfondo) e l'azione selezionata (bordo)
        usando un unico StyleSheet combinato sulla Label per evitare conflitti.
        """
        # --- CONFIGURAZIONE COLORI ---
        c_bg_topk =settings.GRAPH_PALETTE["ACTIONS_CORRELATED"]
        c_border_sel = settings.GRAPH_PALETTE["ACTION_SOURCE"]
        c_transparent = "transparent"
        
        # Pulisci la selezione di default di Qt (quella blu)
        self.list_widget.clearSelection()
        
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            label_widget = self.list_widget.itemWidget(item)
            
            if not label_widget:
                continue

            # Determina gli stati
            is_top_k = row in top_indices
            is_selected = (row == action_selected)
            
            # --- COSTRUZIONE STYLE SHEET ---
            # Partiamo da una base comune (padding e radius)
            style_rules = ["border-radius: 4px;"]
            
            # 1. Gestione SFONDO
            if is_top_k:
                style_rules.append(f"background-color: {c_bg_topk};")
            else:
                style_rules.append(f"background-color: {c_transparent};")
            
            # 2. Gestione BORDO
            if is_selected:
                style_rules.append(f"border-bottom: 2px solid {c_border_sel};")
            else:
                style_rules.append("border: none;")
            
            # Applica lo stile finale
            label_widget.setStyleSheet(" ".join(style_rules))
            
            # Resetta lo sfondo del QListWidgetItem per evitare che interferisca
            item.setBackground(QColor("transparent"))
            

    def highlight_tokens_in_text(self, highlights_per_action, section_of_action_selected):
        """
        highlights_per_action: dict { row_index: set(token_indices) } -> Token Blu
        section_of_action_selected: int (indice del token selezionato nella riga corrente) -> Token Verde
        """
        
        # 1. Recuperiamo la riga attualmente selezionata dall'utente
        current_selected_row = self.list_widget.currentRow()

        # Definizioni colori
        c_text_normal = "white"
        c_text_highlight = settings.GRAPH_PALETTE["TOKEN_CORRELATED"]
        c_text_selected = settings.GRAPH_PALETTE["TOKEN_SOURCE"]
        

        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            label_widget = self.list_widget.itemWidget(item)
            if not label_widget: continue
                
            raw_text = item.data(Qt.ItemDataRole.UserRole)
            sections = raw_text.split("_")
            
            # Verifichiamo se questa riga contiene token da evidenziare in blu
            row_highlights = highlights_per_action.get(row, set())
            
            new_html_parts = []
            common_style="font-weight: bold; border-radius: 2px;"
            
            for i, section in enumerate(sections):
                safe_section = html.escape(section)
                
                # --- CALCOLO STATI ---
                # È un token evidenziato (Blu)?
                is_in_highlight_list = (i in row_highlights)
                
                # È il token attualmente selezionato dall'utente (Verde)?
                # Deve corrispondere sia la riga corrente che l'indice del token
                is_current_selection = (row == current_selected_row and i == section_of_action_selected)
                
                # --- APPLICAZIONE STILI ---
                
                if is_current_selection and is_in_highlight_list:
                    # CASO IBRIDO: Verde su sfondo Bluastro
                    # "Metà e metà": Testo Verde (Selection) + Sfondo Blu (Highlight)
                    style = f"color: {c_text_selected}; background-color: {c_text_highlight};{common_style}"
                    new_html_parts.append(f"<span style='{style}'>{safe_section}</span>")
                
                elif is_current_selection:
                    # SOLO SELEZIONATO: Testo Verde puro
                    style = f"color: {c_text_selected}; {common_style}"
                    new_html_parts.append(f"<span style='{style}'>{safe_section}</span>")
                
                elif is_in_highlight_list:
                    # SOLO EVIDENZIATO: Testo Blu puro
                    style = f"color: {c_text_normal}; background-color: {c_text_highlight}; {common_style}"
                    new_html_parts.append(f"<span style='{style}'>{safe_section}</span>")
                
                else:
                    # NORMALE: Bianco
                    style = f"color: {c_text_normal};"
                    new_html_parts.append(f"<span style='{style}'>{safe_section}</span>")
            
            label_widget.setText(f"{row})"+"_".join(new_html_parts))