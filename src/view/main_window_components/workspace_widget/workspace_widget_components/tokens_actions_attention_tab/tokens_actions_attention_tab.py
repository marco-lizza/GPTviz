from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSplitter, QSpinBox, QComboBox) 
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.config import settings

# Import dei componenti UI
from .action_list_pane import ActionListPane
from .action_graph_pane import ActionGraphPane
from .token_graph_pane import TokenGraphPane

class TokenActionsAttentionView(QWidget):
    """
    Vista principale per l'analisi Token-to-Action.
    Delega la logica di calcolo al ViewModel e gestisce solo l'interfaccia utente.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Riferimento al ViewModel (inizialmente nullo)
        self.view_model = None
        
        # Parametri di visualizzazione
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
        
        # Selettore Head
        self.head_label = QLabel("HEAD:")
        self.head_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        toolbar_layout.addWidget(self.head_label)

        self.head_combo = QComboBox()
        self.head_combo.setStyleSheet(settings.get_stylesheets("QComboBox_style.qss"))
        self.head_combo.currentIndexChanged.connect(self.on_layer_changed)
        toolbar_layout.addWidget(self.head_combo)

        toolbar_layout.addSpacing(15)

        # Selettore Top-K Actions
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

        # Selettore Top-K Tokens
        self.token_top_k_label = QLabel("Token Top-K:")
        self.token_top_k_label.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        toolbar_layout.addWidget(self.token_top_k_label)
        
        self.spin_k_tokens = QSpinBox()
        self.spin_k_tokens.setStyleSheet(settings.get_stylesheets("QSpinBox_style.qss"))
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
        # Sincronizzazione selezione token -> lista
        self.token_graph.token_selector.currentIndexChanged.connect(self.sync_token_highlights)

        self.viz_splitter.addWidget(self.action_graph)
        self.viz_splitter.addWidget(self.token_graph)
        self.viz_splitter.setSizes([400, 400])
        
        r_layout.addWidget(self.viz_splitter)
        self.main_splitter.addWidget(self.right_container)
        self.main_splitter.setSizes([200, 800])

    def set_view_model(self, view_model):
        """
        Imposta il ViewModel e aggiorna l'interfaccia con i nuovi dati.
        Sostituisce il vecchio metodo 'update_data'.
        """
        self.view_model = view_model
        
        if not self.view_model:
            return

        # 1. Popola la lista delle azioni
        self.list_pane.populate(self.view_model.actions)
        
        # 2. Aggiorna il selettore delle Head
        self._update_head_combo()
        
        # 3. Se ci sono head disponibili, seleziona la prima e aggiorna la vista
        if self.view_model.get_num_heads() > 0:
            # Blocchiamo i segnali per evitare trigger doppi durante il setup iniziale
            self.head_combo.blockSignals(True)
            self.head_combo.setCurrentIndex(0)
            self.head_combo.blockSignals(False)
            
            # Forza l'aggiornamento grafico
            self._refresh_view()

    def _update_head_combo(self):
        """Rigenera il ComboBox in base al numero di head nel ViewModel."""
        self.head_combo.blockSignals(True)
        self.head_combo.clear()
        
        if self.view_model:
            num_heads = self.view_model.get_num_heads()
            icon = QIcon("assets/attention_navigator/item_icons/head.svg")
            for i in range(num_heads):
                self.head_combo.addItem(icon, f"Head {i}")
            
        self.head_combo.blockSignals(False)

    # --- EVENTI UI ---

    def on_params_changed(self):
        """Chiamato quando cambiano i valori degli SpinBox (Top-K)."""
        self.k_actions = self.spin_k_actions.value()
        self.k_tokens = self.spin_k_tokens.value()
        self._refresh_view()

    def on_layer_changed(self):
        """Chiamato quando l'utente seleziona una nuova Head."""
        self._refresh_view()

    def _refresh_view(self):
        """Ricarica la vista basandosi sulla selezione corrente nella lista."""
        cur = self.list_pane.get_current_selection()
        if cur: 
            row = self.list_pane.list_widget.row(cur)
            text = cur.data(Qt.ItemDataRole.UserRole)
            self.on_action_list_clicked(row, text)
        else:
            # Se nulla è selezionato, potremmo pulire i grafici
            pass

    def on_action_list_clicked(self, row, text):
        """Gestisce il click su un'azione nella lista."""
        if not self.view_model:
            return

        self.k_actions = self.spin_k_actions.value()
        head_idx = self.head_combo.currentIndex()
        
        # --- RICHIESTA DATI AL VIEWMODEL ---
        # normalize_by_row=True -> Probabilità (Somma righe = 1)
        # normalize_by_row=False -> Densità (Heatmap)
        agg_matrix = self.view_model.get_aggregated_matrix(head_idx, normalize_by_row=True)
        
        if agg_matrix is None:
            return

        # Disegna il grafo azioni
        top_indices = self.action_graph.draw_graph(
            row, 
            text, 
            agg_matrix, 
            self.view_model.actions, 
            self.k_actions
        )
        
        # Evidenzia le azioni collegate nella lista
        self.list_pane.highlight_actions(top_indices, row)
        
        # Aggiorna il pannello inferiore dei token
        self.prepare_token_pane(row)

    def prepare_token_pane(self, action_idx):
        """Prepara il grafo token in base all'azione selezionata."""
        if not self.view_model:
            return

        head_idx = self.head_combo.currentIndex()
        if head_idx < 0: 
            return
        
        self.k_tokens = self.spin_k_tokens.value()
        
        # Recupera matrice raw e mapping dal ViewModel
        raw_matrix = self.view_model.get_raw_matrix(head_idx)
        action_indices = self.view_model.action_map[action_idx]
        action_name = self.view_model.actions[action_idx]
        
        # Carica i dati nel grafo token
        self.token_graph.load_action_tokens(
            action_name, 
            raw_matrix, 
            self.view_model.tokens, 
            action_indices, 
            self.k_tokens
        )
        
        self.sync_token_highlights(0)

    def sync_token_highlights(self, index=None):
        """
        Evidenzia nella lista delle azioni le parti di testo corrispondenti 
        ai token visualizzati nel grafo inferiore.
        """
        if not self.view_model:
            return

        top_token_indices = self.token_graph.current_top_targets

        # Mappa Token Index -> (Row Index, Section Index)
        # Usa action_map del ViewModel
        highlights_per_action = {}
        
        for top_index in top_token_indices:
            for row_idx, token_indices in enumerate(self.view_model.action_map):
                for section_idx, val in enumerate(token_indices):
                    if top_index == val:
                        if row_idx not in highlights_per_action:
                            highlights_per_action[row_idx] = set()
                        highlights_per_action[row_idx].add(section_idx)
        
        self.list_pane.highlight_tokens_in_text(highlights_per_action, index)