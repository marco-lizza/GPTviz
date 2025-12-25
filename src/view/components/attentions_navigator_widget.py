from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from src.config import settings

class Attention_navigator_widget(QTreeWidget):
    """
    Widget di navigazione gerarchica per selezionare specifiche 'Attention Heads'.

    Visualizza una struttura ad albero a tre livelli che riflette l'architettura
    interna del modello Transformer:
    1. **Iterazioni** (Token generati nel tempo).
    2. **Livelli** (Layers del modello).
    3. **Teste** (Attention Heads specifiche).

    Ogni nodo foglia (Head) contiene metadati nascosti che permettono di identificare
    univocamente la matrice di attenzione da caricare.

    Signals:
        head_clicked (int, int, int): Emesso quando l'utente clicca su una testa finale.
            Payload: `(iter_idx, lev_idx, head_idx)`.
    """

    head_clicked = pyqtSignal(int, int, int)

    def __init__(self):
        """
        Inizializza l'albero di navigazione, lo stile e le impostazioni di selezione.
        """
        super().__init__()
        
        # Configurazione Visuale
        self.setHeaderHidden(True)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.setUniformRowHeights(True)
        self.setIndentation(20) 
        
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Applicazione Stile
        stylesheet = settings.get_stylesheets("QTreeWidget_style.qss", "QScrollBar_style.qss")
        self.setStyleSheet(stylesheet)
        
        self.itemClicked.connect(self._on_item_clicked)
        self.setMouseTracking(True) 

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Gestisce l'evento di click su un nodo dell'albero.

        Verifica se il nodo cliccato è una 'head' (foglia). In tal caso, estrae
        gli indici salvati nei ruoli dati custom (`UserRole`) ed emette il segnale
        per aggiornare il Workspace.

        Data Mapping (UserRole):
            * UserRole + 0: Tipo di item ("head", "level", "iteration").
            * UserRole + 1: Indice Iterazione.
            * UserRole + 2: Indice Livello.
            * UserRole + 3: Indice Testa.

        Args:
            item (QTreeWidgetItem): L'elemento cliccato.
            column (int): La colonna cliccata.
        """
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_type == "head":
            # Estrazione dei metadati nascosti
            iter_idx = item.data(0, Qt.ItemDataRole.UserRole + 1)
            lev_idx  = item.data(0, Qt.ItemDataRole.UserRole + 2)
            head_idx = item.data(0, Qt.ItemDataRole.UserRole + 3)
            
            # Notifica al controller
            self.head_clicked.emit(iter_idx, lev_idx, head_idx)

    def mouseMoveEvent(self, event):
        """
        Gestisce il feedback visivo del cursore mouse. 
        """
        item = self.itemAt(event.pos())

        # Se l'item esiste e non ha figli, è una foglia (Head) selezionabile
        if item and item.childCount() == 0:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(event)

    def update_sidebar(self, num_iterations: int, num_levels: int, num_heads: int):
        """
        Rigenera l'intera struttura dell'albero in base alle dimensioni del modello.

        Esegue tre cicli annidati per costruire la gerarchia completa e popolare
        ogni nodo foglia con i metadati necessari per il recupero dei dati.

        Struttura generata:
        Iterazione 0
            └── Livello 0
                ├── Head 0  <-- Contiene (0, 0, 0)
                └── Head 1  <-- Contiene (0, 0, 1)
        
        Args:
            num_iterations (int): Numero totale di token/passi temporali.
            num_levels (int): Numero di layer del Transformer.
            num_heads (int): Numero di teste per layer.
        """
        self.clear()

        # --- Livello 1: Iterazioni ---
        for i in range(num_iterations):
            iter_item = QTreeWidgetItem(self)
            iter_item.setText(0, f"Iterazione {i}")
            iter_item.setData(0, Qt.ItemDataRole.UserRole, "iteration")
            iter_item.setIcon(0, QIcon("assets/attention_navigator/item_icons/iteration.svg"))
            
            # --- Livello 2: Livelli (Layer) ---
            for l in range(num_levels):
                level_item = QTreeWidgetItem(iter_item)
                level_item.setText(0, f"Livello {l}")
                level_item.setData(0, Qt.ItemDataRole.UserRole, "level")
                level_item.setIcon(0, QIcon("assets/attention_navigator/item_icons/level.svg"))
                
                # --- Livello 3: Heads ---
                for h in range(num_heads):
                    head_item = QTreeWidgetItem(level_item)
                    head_item.setText(0, f"Head {h}")
                    
                    # Salviamo i metadati importanti in questo item (Leaf Node)
                    head_item.setData(0, Qt.ItemDataRole.UserRole, "head")      # Tipo
                    head_item.setData(0, Qt.ItemDataRole.UserRole + 1, i)       # Iterazione
                    head_item.setData(0, Qt.ItemDataRole.UserRole + 2, l)       # Livello
                    head_item.setData(0, Qt.ItemDataRole.UserRole + 3, h)       # Testa
                    
                    head_item.setIcon(0, QIcon("assets/attention_navigator/item_icons/head.svg"))