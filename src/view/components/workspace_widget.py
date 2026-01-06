from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import Qt

from .attention_heatmap_tab import AttentionHeatmapView
from .tokens_attention_tab import TokenAttentionView
from .attentions_level_tab import MultiHeadAttentionView

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
        grid_view (MultiHeadAttentionView): Tab per l'analisi del livello intero.
        heatmap_view (AttentionHeatmapView): Tab per la matrice di calore.
        token_view (TokenAttentionView): Tab per l'analisi dei token.
        tabs (QTabWidget): Il widget contenitore delle schede (esiste solo nello stato Active).
    """

    def __init__(self):
        """Inizializza il frame e imposta lo stato iniziale (Idle)."""
        super().__init__()

        # Creazione del layout verticale principale che conterrà o la Label o i Tab
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Vengono tenuti in memoria per poterli aggiornare senza ricrearli ogni volta.
        self.grid_view = None
        self.heatmap_view = None
        self.token_view = None
        self.tabs = None
        
        # Imposta lo stato iniziale (mostra il messaggio "No level selected")
        self.reset_view()

    def reset_view(self):
        """
        Ripristina lo stato 'Idle' (Nessuna selezione).

        Svuota completamente il layout corrente (rimuovendo grafici o tab)
        e inserisce una singola etichetta di testo centrata.
        Utile quando si cambia file o si vuole pulire la schermata.
        """
        # Rimuove tutti i widget attuali dal layout
        self._clear_main_layout()
        
        # Crea l'etichetta di placeholder
        label = QLabel("No level selected")
        
        stylesheet = settings.get_stylesheets("QLabel_style.qss")
        self.setStyleSheet(stylesheet)
        
        # Centra il testo
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(label)
        
        self.grid_view = MultiHeadAttentionView()
        self.heatmap_view = AttentionHeatmapView()
        self.token_view = TokenAttentionView()
        self.tabs = None

    def visualize_attentions(self, heads_attention_level, token_list):
        """
        Riceve i dati e passa allo stato 'Visualization' (Tabs).

        Args:
            heads_attention_level (list[torch.Tensor]): Le matrici di attenzione del livello da visualizzare.
            token_list (list[str]): I tokens del problema attualmente visualizzato
        """
        # Controllo di sicurezza: se non ci sono dati, non fare nulla
        if heads_attention_level is None:
            return

        # Lazy Initialization: Crea la struttura a schede (QTabWidget) solo se non esiste già.
        if self.tabs is None:
            self._switch_to_tab_mode()

        if self.grid_view:
            self.grid_view.update_data(heads_attention_level)

        if self.heatmap_view:
            self.heatmap_view.update_data(heads_attention_level, token_list)
        
        if self.token_view:
            self.token_view.update_data(heads_attention_level, token_list)
        

    def _switch_to_tab_mode(self):
        """
        Costruisce la gerarchia dei Tab e istanzia le viste specifiche.

        Questo metodo viene chiamato una sola volta quando si passa dallo stato
        Idle allo stato Visualization.
        """
        # Pulisce il layout (rimuove la Label "Nessuna head selezionata")
        self._clear_main_layout()
        
        # Crea il widget delle schede
        self.tabs = QTabWidget()
        
        stylesheet = settings.get_stylesheets("QTabWidget_style.qss")
        self.setStyleSheet(stylesheet)
        
        self.tabs.setDocumentMode(True) 
        
        self.main_layout.addWidget(self.tabs)
        
        self.tabs.addTab(self.grid_view, "Level view")
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