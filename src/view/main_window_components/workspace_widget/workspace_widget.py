from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import Qt

from .workspace_widget_components.heatmap_tabs.attention_heatmap_tab import AttentionHeatmapView
from .workspace_widget_components.tokens_actions_attention_tab.tokens_actions_attention_tab import TokenActionsAttentionView
from .workspace_widget_components.heatmap_tabs.attentions_level_tab import MultiHeadAttentionView

from src.config import settings

from src.view.main_window_components.main_window_viewmodels.action_attention_view_model import ActionAttentionViewModel

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
        token_action_view (TokenActionsAttentionView): Tab per l'analisi dei token e delle azioni.
        tabs (QTabWidget): Il widget contenitore delle schede (esiste solo nello stato Active).
    """

class WorkspaceView(QFrame):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Istanza del ViewModel
        self.view_model = ActionAttentionViewModel()
        
        self.grid_view = None
        self.heatmap_view = None
        self.token_action_view = None # La tua vista azioni
        self.tabs = None
        
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
        self.token_action_view = TokenActionsAttentionView()
        self.tabs = None

    def visualize_attentions(self, heads_attention_level, token_list, action_list):
        """
        Riceve i dati e passa allo stato 'Visualization' (Tabs).

        Args:
            heads_attention_level (list[torch.Tensor]): Le matrici di attenzione del livello da visualizzare.
            token_list (list[str]): I tokens del problema attualmente visualizzato
            action_list (list[str]): Le actions del problema attualmente visualizzato
        """
        if heads_attention_level is None: return

        # 1. Carica i dati nel ViewModel
        self.view_model.load_data(heads_attention_level, token_list, action_list)

        if self.tabs is None:
            self._switch_to_tab_mode()

        # 2. Passa il ViewModel a TUTTE le viste
        # Ognuna ora sa come gestirsi autonomamente
        if self.grid_view:
            self.grid_view.set_view_model(self.view_model)

        if self.heatmap_view:
            self.heatmap_view.set_view_model(self.view_model)
        
        if self.token_action_view:
            self.token_action_view.set_view_model(self.view_model)
        

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

        self.grid_view = MultiHeadAttentionView()
        self.heatmap_view = AttentionHeatmapView()
        self.token_action_view = TokenActionsAttentionView()
        
        self.tabs.addTab(self.grid_view, "Level view")
        self.tabs.addTab(self.heatmap_view, "Heatmap")
        self.tabs.addTab(self.token_action_view, "Tokens Attention")

    def _clear_main_layout(self):
        """
        Rimuove e distrugge tutti i widget presenti nel layout principale.
        """
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()