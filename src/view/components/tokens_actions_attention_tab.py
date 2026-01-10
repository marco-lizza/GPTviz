import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSplitter, QSpinBox, QComboBox) 
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.config import settings

# Import dei moduli refactorizzati
from .ui.action_list_pane import ActionListPane
from .ui.action_graph_pane import ActionGraphPane
from .ui.token_graph_pane import TokenGraphPane

class TokenActionsAttentionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.raw_attention_tensors = []
        self.aggregated_matrices = []
        self.tokens = []
        self.actions = []
        self.action_map = [] # ActionIndex -> [TokenIndices]
        
        self.k_actions = 3
        self.k_tokens = 5
        
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # --- TOOLBAR ---
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 5, 5, 0)
        
        toolbar_layout.addWidget(QLabel("HEAD:"))
        self.head_combo = QComboBox()
        self.head_combo.setStyleSheet( settings.get_stylesheets("QComboBox_style.qss"))
        self.head_combo.currentIndexChanged.connect(self.on_layer_changed)
        toolbar_layout.addWidget(self.head_combo)

        toolbar_layout.addSpacing(15)

        self.action_top_k_label = QLabel("Action Top-K:")
        self.action_top_k_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))

        toolbar_layout.addWidget(self.action_top_k_label)
        self.spin_k_actions = QSpinBox() 
        self.spin_k_actions.setStyleSheet( settings.get_stylesheets("QSpinBox_style.qss"))
        self.spin_k_actions.setRange(1, 20)
        self.spin_k_actions.setValue(self.k_actions)
        self.spin_k_actions.valueChanged.connect(self.on_params_changed)
        toolbar_layout.addWidget(self.spin_k_actions)

        self.token_top_k_label = QLabel("Token Top-K:")
        self.token_top_k_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))

        toolbar_layout.addSpacing(15)
        toolbar_layout.addWidget(self.token_top_k_label)
        self.spin_k_tokens = QSpinBox()
        self.spin_k_tokens.setStyleSheet( settings.get_stylesheets("QSpinBox_style.qss"))
        self.spin_k_tokens.setRange(1, 20)
        self.spin_k_tokens.setValue(self.k_tokens)
        self.spin_k_tokens.valueChanged.connect(self.on_params_changed)
        toolbar_layout.addWidget(self.spin_k_tokens)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # --- SPLITTER PRINCIPALE ---
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # 1. Lista Azioni (Sinistra)
        self.list_pane = ActionListPane()
        self.list_pane.action_clicked.connect(self.on_action_list_clicked)
        self.main_splitter.addWidget(self.list_pane)

        # 2. Area Visualizzazione (Destra)
        self.right_container = QWidget()
        r_layout = QVBoxLayout(self.right_container)
        r_layout.setContentsMargins(0,0,0,0)
        
        self.viz_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 2a. Grafo Azioni (Top)
        self.action_graph = ActionGraphPane()
        
        # 2b. Grafo Token (Bottom)
        self.token_graph = TokenGraphPane()
        # Quando il grafo token aggiorna i suoi dati, vogliamo evidenziare le parole nella lista
        self.token_graph.token_selector.currentIndexChanged.connect(self.sync_token_highlights)

        self.viz_splitter.addWidget(self.action_graph)
        self.viz_splitter.addWidget(self.token_graph)
        self.viz_splitter.setSizes([400, 400])
        
        r_layout.addWidget(self.viz_splitter)
        self.main_splitter.addWidget(self.right_container)
        self.main_splitter.setSizes([200, 800])

    # --- LOGICA DATI ---
    def update_data(self, attention_tensors, token_list, action_list):
        if not isinstance(attention_tensors, list):
            self.raw_attention_tensors = [np.array(attention_tensors)]
        else:
            self.raw_attention_tensors = [np.array(t) for t in attention_tensors]

        self.tokens = token_list
        self.actions = action_list
        
        max_tokens = self.raw_attention_tensors[0].shape[0] if self.raw_attention_tensors else 0
        self.action_map = []
        current_idx = 0
        for action in action_list:
            n_parts = len(action.split('_'))
            indices = [current_idx + i for i in range(n_parts) if current_idx + i < max_tokens]
            self.action_map.append(indices)
            current_idx += n_parts

        self.aggregated_matrices = []
        for raw_matrix in self.raw_attention_tensors:
            try:
                agg = self._calculate_aggregated_matrix(raw_matrix)
                self.aggregated_matrices.append(agg)
            except:
                n = len(self.actions)
                self.aggregated_matrices.append(np.zeros((n,n)))

        self._update_head_combo()
        self.list_pane.populate(self.actions)

    def _calculate_aggregated_matrix(self, raw_matrix):
        n = len(self.actions)
        res = np.zeros((n, n))
        for r in range(n):
            r_idx = self.action_map[r]
            if not r_idx: continue
            for c in range(n):
                c_idx = self.action_map[c]
                if not c_idx: continue
                block = raw_matrix[np.ix_(r_idx, c_idx)]
                res[r, c] = np.mean(block) if block.size > 0 else 0
        return res

    def _update_head_combo(self):
        self.head_combo.blockSignals(True)
        self.head_combo.clear()
        icon = QIcon("assets/attention_navigator/item_icons/head.svg")
        for i in range(len(self.aggregated_matrices)):
            self.head_combo.addItem(icon, f"Head {i}")
        self.head_combo.blockSignals(False)

    # --- EVENTI UI ---
    def on_params_changed(self):
        self.k_actions = self.spin_k_actions.value()
        self.k_tokens = self.spin_k_tokens.value()
        self._refresh_view()

    def on_layer_changed(self):
        self._refresh_view()

    def _refresh_view(self):
        cur = self.list_pane.get_current_selection()
        if cur: 
            row = self.list_pane.list_widget.row(cur)
            text = cur.data(Qt.ItemDataRole.UserRole)
            self.on_action_list_clicked(row, text)

    def on_action_list_clicked(self, row, text):
        self.k_actions = self.spin_k_actions.value()
        
        head_idx = self.head_combo.currentIndex()
        if head_idx < 0: return

        # 1. Aggiorna Grafo Azioni
        agg_matrix = self.aggregated_matrices[head_idx]
        top_indices = self.action_graph.draw_graph(row, text, agg_matrix, 
                                                   self.actions, self.k_actions)
        
        # 2. Evidenzia nella lista
        self.list_pane.highlight_actions(top_indices,row)
        
        # 3. Aggiorna Pannello Token
        self.prepare_token_pane(row)

    def prepare_token_pane(self, action_idx):
        """Prepara il grafo token in base all'azione selezionata (da lista o grafo azioni)."""
        head_idx = self.head_combo.currentIndex()
        if head_idx < 0: return
        
        self.k_tokens = self.spin_k_tokens.value()
        raw_matrix = self.raw_attention_tensors[head_idx]
        
        action_indices = self.action_map[action_idx]
        action_name = self.actions[action_idx]
        
        self.token_graph.load_action_tokens(action_name, raw_matrix, self.tokens, 
                                           action_indices, self.k_tokens)
        
        self.sync_token_highlights(0)

    def sync_token_highlights(self,index=None):
        """Prende i target del grafo token ed evidenzia le parti di testo nella lista."""
        top_token_indices = self.token_graph.current_top_targets

        # Mappa Token Index -> Row Index & Section Index
        highlights_per_action = {}
        for top_index in top_token_indices:
            for row_idx, token_indices in enumerate(self.action_map):
                for section_idx, val in enumerate(token_indices):
                    if top_index == val:
                        if row_idx not in highlights_per_action:
                            highlights_per_action[row_idx] = set()
                        highlights_per_action[row_idx].add(section_idx)
        
        self.list_pane.highlight_tokens_in_text(highlights_per_action,index)