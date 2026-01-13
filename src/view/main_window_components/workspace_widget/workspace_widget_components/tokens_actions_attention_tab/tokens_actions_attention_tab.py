import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSplitter, QSpinBox, QComboBox, QCheckBox) 
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.config import settings

from .action_list_pane import ActionListPane
from .action_graph_pane import ActionGraphPane
from .token_graph_pane import TokenGraphPane

class TokenActionsAttentionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view_model = None
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
        
        self.head_label = QLabel("HEAD:")
        self.head_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        toolbar_layout.addWidget(self.head_label)

        self.head_combo = QComboBox()
        self.head_combo.setStyleSheet(settings.get_stylesheets("QComboBox_style.qss"))
        self.head_combo.currentIndexChanged.connect(self.on_layer_changed)
        toolbar_layout.addWidget(self.head_combo)

        toolbar_layout.addSpacing(15)

        self.action_top_k_label = QLabel("Action Top-K:")
        self.action_top_k_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        toolbar_layout.addWidget(self.action_top_k_label)
        
        self.spin_k_actions = QSpinBox() 
        self.spin_k_actions.setStyleSheet(settings.get_stylesheets("QSpinBox_style.qss"))
        self.spin_k_actions.setRange(1, 20)
        self.spin_k_actions.setValue(self.k_actions)
        self.spin_k_actions.valueChanged.connect(self.on_params_changed)
        toolbar_layout.addWidget(self.spin_k_actions)

        toolbar_layout.addSpacing(15)

        self.token_top_k_label = QLabel("Token Top-K:")
        self.token_top_k_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        toolbar_layout.addWidget(self.token_top_k_label)
        
        self.spin_k_tokens = QSpinBox()
        self.spin_k_tokens.setStyleSheet(settings.get_stylesheets("QSpinBox_style.qss"))
        self.spin_k_tokens.setRange(1, 20)
        self.spin_k_tokens.setValue(self.k_tokens)
        self.spin_k_tokens.valueChanged.connect(self.on_params_changed)
        toolbar_layout.addWidget(self.spin_k_tokens)

        toolbar_layout.addSpacing(15)

        self.chk_show_links = QCheckBox("Show Ex Links")
        self.chk_show_links.setStyleSheet(settings.get_stylesheet("QCheckBox_style.qss"))
        self.chk_show_links.setChecked(False)
        self.chk_show_links.stateChanged.connect(self.on_params_changed)
        toolbar_layout.addWidget(self.chk_show_links)
        self.chk_show_links.setVisible(False)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)

        self.list_pane = ActionListPane()
        self.list_pane.action_clicked.connect(self.on_action_list_clicked)
        self.main_splitter.addWidget(self.list_pane)

        self.right_container = QWidget()
        r_layout = QVBoxLayout(self.right_container)
        r_layout.setContentsMargins(0,0,0,0)
        
        self.viz_splitter = QSplitter(Qt.Orientation.Vertical)
        self.action_graph = ActionGraphPane()
        self.token_graph = TokenGraphPane()
        self.token_graph.token_selector.currentIndexChanged.connect(self.sync_token_highlights)

        self.viz_splitter.addWidget(self.action_graph)
        self.viz_splitter.addWidget(self.token_graph)
        self.viz_splitter.setSizes([400, 400])
        
        r_layout.addWidget(self.viz_splitter)
        self.main_splitter.addWidget(self.right_container)
        self.main_splitter.setSizes([200, 800])

    def set_view_model(self, view_model):
        self.view_model = view_model
        if not self.view_model: return
        self.list_pane.populate(self.view_model.actions)
        self._update_head_combo()
        if self.view_model.get_num_heads() > 0:
            self.head_combo.blockSignals(True)
            self.head_combo.setCurrentIndex(0)
            self.head_combo.blockSignals(False)
            self._refresh_view()
            
    def _update_head_combo(self):
        self.head_combo.blockSignals(True)
        self.head_combo.clear()
        if self.view_model:
            num_heads = self.view_model.get_num_heads()
            icon = QIcon("assets/attention_navigator/item_icons/head.svg")
            for i in range(num_heads):
                self.head_combo.addItem(icon, f"Head {i}")
        self.head_combo.blockSignals(False)

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
        if not self.view_model:
            return

        self.k_actions = self.spin_k_actions.value()
        head_idx = self.head_combo.currentIndex()
        
        agg_matrix = self.view_model.get_aggregated_matrix(head_idx, normalize_by_row=True)
        if agg_matrix is None: return

        show_gt = self.chk_show_links.isChecked()
        gt_indices = set()
        matrices_arg = None
        
        # Controlliamo se il ViewModel ha l'attributo e se non è None
        if hasattr(self.view_model, 'action_link_matrices') and self.view_model.action_link_matrices is not None:

            self.chk_show_links.setVisible(True)
            
            # Se la checkbox è attiva, prepariamo i dati
            if show_gt:
                matrices_arg = self.view_model.action_link_matrices

                temp_matrix = matrices_arg[0] if isinstance(matrices_arg, list) else matrices_arg
                
                if temp_matrix is not None:
                    try:
                        gt_indices = set(np.where(temp_matrix[row] == 1)[0])
                    except Exception as e:
                        print(f"Errore lettura GT matrix: {e}")
                        gt_indices = set()

        top_indices = self.action_graph.draw_graph(
            row, 
            text, 
            agg_matrix, 
            self.view_model.actions, 
            self.k_actions,
            matrices_arg 
        )
        
        # Aggiorna la lista
        self.list_pane.highlight_actions(top_indices, row, gt_indices, show_gt)
        
        self.prepare_token_pane(row)

    def prepare_token_pane(self, action_idx):
        if not self.view_model: return
        head_idx = self.head_combo.currentIndex()
        if head_idx < 0: return
        self.k_tokens = self.spin_k_tokens.value()
        raw_matrix = self.view_model.get_raw_matrix(head_idx)
        action_indices = self.view_model.action_map[action_idx]
        action_name = self.view_model.actions[action_idx]
        self.token_graph.load_action_tokens(action_name, raw_matrix, self.view_model.tokens, action_indices, self.k_tokens)
        self.sync_token_highlights(0)

    def sync_token_highlights(self, index=None):
        if not self.view_model: return
        top_token_indices = self.token_graph.current_top_targets
        highlights_per_action = {}
        for top_index in top_token_indices:
            for row_idx, token_indices in enumerate(self.view_model.action_map):
                for section_idx, val in enumerate(token_indices):
                    if top_index == val:
                        if row_idx not in highlights_per_action:
                            highlights_per_action[row_idx] = set()
                        highlights_per_action[row_idx].add(section_idx)
        self.list_pane.highlight_tokens_in_text(highlights_per_action, index)