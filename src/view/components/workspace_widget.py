from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import Qt

from .attention_heatmap_tab import AttentionHeatmapView
from .tokens_attention_tab import TokenAttentionView

from src.config import settings

class WorkspaceView(QFrame):
    """
    Gestisce l'area centrale di visualizzazione (Workspace).

    Questa classe agisce come un contenitore dinamico che cambia il proprio layout
    in base allo stato dell'applicazione:
    
    States:
        1. **Idle State**: Quando nessun dato è selezionato, mostra un messaggio
           di cortesia ("Nessuna head selezionata").
        2. **Visualization State**: Quando arriva un tensore, sostituisce il messaggio
           con un `QTabWidget` contenente le viste specializzate (Heatmap, Tokens).

    Attributes:
        heatmap_view (AttentionHeatmapView): Tab per la matrice di calore.
        token_view (TokenAttentionView): Tab per l'analisi dei token.
        tabs (QTabWidget): Il widget contenitore delle schede (esiste solo nello stato Active).
    """

    def __init__(self):
        """Inizializza il frame e imposta lo stato iniziale (Idle)."""
        super().__init__()

        """
        DA DEFINIRE
        stylesheet = settings.get_stylesheet("workspace_style.qss")
        self.setStyleSheet(stylesheet)
        """
        
        self.main_layout = QVBoxLayout()
        # Rimuove i margini per permettere ai widget di occupare tutto lo spazio
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        
        # Riferimenti ai widget figli (inizializzati a None)
        self.heatmap_view = None
        self.token_view = None
        self.tabs = None
        
        # Imposta lo stato iniziale
        self.reset_view()

    def reset_view(self):
        """
        Ripristina lo stato 'Idle' (Nessuna selezione).

        Svuota completamente il layout corrente (rimuovendo grafici o tab)
        e inserisce una singola etichetta di testo centrata.
        Utile quando si cambia file o si vuole pulire la schermata.
        """
        self._clear_main_layout()
        
        label = QLabel("Nessuna head selezionata")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Stile inline per il placeholder (può essere spostato nel QSS)
        label.setStyleSheet("color: #666; font-size: 24px; font-weight: bold; border: none;")
        self.main_layout.addWidget(label)
        
        # Resetta i riferimenti per liberare memoria e indicare lo stato inattivo
        self.heatmap_view = None
        self.token_view = None
        self.tabs = None

    def visualize_attentions_matrix(self, attention_tensor):
        """
        Riceve i dati e passa allo stato 'Visualization' (Tabs).

        Args:
            attention_tensor (torch.Tensor): La matrice di attenzione da visualizzare.
        """
        if attention_tensor is None:
            return

        # Lazy Initialization: Crea i tab solo se non esistono già
        if self.tabs is None:
            self._switch_to_tab_mode()

        # Propaga i dati alle viste specifiche
        if self.heatmap_view:
            self.heatmap_view.update_data(attention_tensor)
        
        if self.token_view:
            self.token_view.update_data(attention_tensor)

    def _switch_to_tab_mode(self):
        """
        Costruisce la gerarchia dei Tab e istanzia le viste specifiche.

        Questo metodo viene chiamato una sola volta quando si passa dallo stato
        Idle allo stato Visualization.
        """
        self._clear_main_layout()
        
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True) 
        
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.addWidget(self.tabs)
        
        # Istanziazione dei componenti grafici reali
        self.heatmap_view = AttentionHeatmapView()
        self.token_view = TokenAttentionView()
        
        self.tabs.addTab(self.heatmap_view, "Heatmap")
        self.tabs.addTab(self.token_view, "Tokens Attention")

    def _clear_main_layout(self):
        """
        Rimuove e distrugge tutti i widget presenti nel layout principale.
        """
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()