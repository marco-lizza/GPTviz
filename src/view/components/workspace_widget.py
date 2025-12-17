from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import Qt

from .attention_heatmap_tab import AttentionHeatmapView
from .tokens_attention_tab import TokenAttentionView

class WorkspaceView(QFrame):
    def __init__(self):
        super().__init__()
        
        # Stile globale per il Workspace e i Tab
        self.setStyleSheet("""
            QFrame { background-color: #333333; }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab {
                background: #2b2b2b;
                color: #aaa;
                padding: 8px 12px;
                border: 1px solid #444;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #444;
                color: white;
                border-bottom: 2px solid #0078d7;
            }
        """)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        
        self.heatmap_view = None
        self.token_view = None
        self.tabs = None
        
        self.reset_view()

    def reset_view(self):
        """Torna allo stato 'Nessuna head selezionata'."""
        self._clear_main_layout()
        
        label = QLabel("Nessuna head selezionata")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666; font-size: 24px; font-weight: bold; border: none;")
        self.main_layout.addWidget(label)
        
        self.heatmap_view = None
        self.token_view = None
        self.tabs = None

    def visualize_attentions_matrix(self, attention_tensor):
        """Gestisce il passaggio alla modalità Tab e delega l'aggiornamento ai figli."""
        if attention_tensor is None:
            return

        if self.tabs is None:
            self._switch_to_tab_mode()

        if self.heatmap_view:
            self.heatmap_view.update_data(attention_tensor)
        
        if self.token_view:
            self.token_view.update_data(attention_tensor)

    def _switch_to_tab_mode(self):
        """Costruisce i Tab e istanzia i componenti figli."""
        self._clear_main_layout()
        
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        self.heatmap_view = AttentionHeatmapView()
        self.token_view = TokenAttentionView()
        
        self.tabs.addTab(self.heatmap_view, "Heatmap")
        self.tabs.addTab(self.token_view, "Tokens Attention")

    def _clear_main_layout(self):
        """Svuota il layout principale."""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()