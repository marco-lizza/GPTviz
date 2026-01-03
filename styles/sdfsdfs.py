from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import Qt

from .attention_heatmap_tab import AttentionHeatmapView
from .tokens_attention_tab import TokenAttentionView

from src.config import settings

class WorkspaceView(QFrame):
    """
    Gestisce l'area centrale di visualizzazione (Workspace).

    Questa classe agisce come un contenitore dinamico (State Machine) che cambia 
    il proprio layout e contenuto in base allo stato dell'applicazione.
    
    Stati:
        1. **Idle State**: Nessun dato selezionato. Mostra un placeholder (QLabel).
        2. **Visualization State**: Dati caricati. Mostra i grafici organizzati in schede (QTabWidget).

    """

    def __init__(self):
        """
        Inizializza il frame, configura il layout base e imposta lo stato iniziale.
        """
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self.heatmap_view = None
        self.token_view = None
        self.tabs = None
        
        # Avvia lo stato di default (Idle)
        self.reset_view()

    def reset_view(self):
        """
        Ripristina lo stato 'Idle' (Nessuna selezione).

        Logica:
        1. Svuota il layout corrente (rimuove grafici o tab esistenti).
        2. Crea una Label di cortesia al centro.
        3. Resetta le variabili interne per liberare memoria.
        """
        self._clear_main_layout()
        
        # Creazione del Placeholder
        label = QLabel("Nessuna head selezionata")
        self.setStyleSheet(settings.get_stylesheet("QLabel_style.qss"))
        
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(label)
        
        self.heatmap_view = AttentionHeatmapView()
        self.token_view = TokenAttentionView()
        self.tabs = None

    def visualize_attentions(self, heads_attention_level, token_list):
        """
        Transizione allo stato 'Visualization'.
        Riceve i dati e popola le viste.

        Args:
            heads_attention_level (list[torch.Tensor]): Lista delle matrici di attenzione.
            token_list (list[str]): Lista dei token corrispondenti.
        """
        if heads_attention_level is None:
            return

        # Costruiamo la struttura a schede (QTabWidget) solo se non esiste già.
        if self.tabs is None:
            self._switch_to_tab_mode()

        if self.heatmap_view:
            self.heatmap_view.update_data(heads_attention_level, token_list)
        
        if self.token_view:
            # DA DEFINIRE
            self.token_view.update_data(heads_attention_level[1], token_list)

    def _switch_to_tab_mode(self):
        """
        Costruisce la gerarchia dei Tab e inserisce le viste nel layout.
        Viene chiamato una sola volta quando si passa da Idle -> Active.
        """
        # Rimuove la Label "Nessuna head selezionata"
        self._clear_main_layout()
        
        # Configurazione QTabWidget
        self.tabs = QTabWidget()
        
        self.tabs.setStyleSheet(settings.get_stylesheet("QTabWidget_style.qss"))
        self.main_layout.addWidget(self.tabs)
        
        # Popola le schede con le view
        self.tabs.addTab(self.heatmap_view, "Heatmap")
        self.tabs.addTab(self.token_view, "Tokens Attention")

    def _clear_main_layout(self):
        """
        Utility per pulire il layout.
        """
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()