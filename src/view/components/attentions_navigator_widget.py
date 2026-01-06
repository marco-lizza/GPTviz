from PyQt6.QtWidgets import (QWidget, QTreeWidget, QTreeWidgetItem, 
                             QAbstractItemView, QLabel, QStackedLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from src.config import settings

class InternalTreeWidget(QTreeWidget):
    """
    Sottoclasse di QTreeWidget personalizzata per gestire comportamenti specifici
    di UI come il tracking del mouse e cursori custom.
    """
    def __init__(self):
        """
        Inizializza il widget dell'albero con le impostazioni di stile e comportamento.
        Configura l'intestazione nascosta, l'altezza uniforme delle righe e la modalità di selezione singola.
        """
        super().__init__()
        self.setMouseTracking(True)
        self.setHeaderHidden(True)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.setUniformRowHeights(True)
        self.setIndentation(20)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def mouseMoveEvent(self, event):
        """
        Gestisce il movimento del mouse per modificare il cursore.
        Mostra un cursore a mano (PointingHandCursor) quando si passa sopra un nodo foglia,
        altrimenti mostra il cursore standard (ArrowCursor).
        """
        item = self.itemAt(event.pos())
        # Se l'item esiste e non ha figli, è una foglia selezionabile
        if item and item.childCount() == 0:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)


class Attention_navigator_widget(QWidget):
    """
    Widget contenitore che alterna tra un messaggio di stato (Label)
    e l'albero di navigazione (Tree).
    """

    level_clicked = pyqtSignal(int, int)

    def __init__(self):
        """
        Inizializza il widget di navigazione configurando il layout a stack.
        Crea le due viste principali (etichetta informativa e albero) e imposta lo stato iniziale.
        """
        super().__init__()
        
        # --- Layout Principale (Stack) ---
        # QStackedLayout permette di sovrapporre widget e mostrarne solo uno alla volta
        self.stack_layout = QStackedLayout(self)
        
        # --- Label (Stato Vuoto) ---
        self.info_label = QLabel("No file selected")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Applica stile Label
        lbl_style = settings.get_stylesheets("QLabel_style.qss")
        self.info_label.setStyleSheet(lbl_style)
        
        # --- Tree (Navigatore) ---
        self.tree = InternalTreeWidget()
        # Applica stile Tree
        tree_style = settings.get_stylesheets("QTreeWidget_style.qss", "QScrollBar_style.qss")
        self.tree.setStyleSheet(tree_style)
        
        self.tree.itemClicked.connect(self._on_item_clicked)
        
        self.stack_layout.addWidget(self.info_label) 
        self.stack_layout.addWidget(self.tree)

        # Stato iniziale
        self.reset_view()

    def reset_view(self):
        """
        Ripristina la vista allo stato iniziale 'nessun file selezionato'.
        Svuota il contenuto dell'albero e attiva l'indice 0 del layout a stack (l'etichetta).
        """
        self.tree.clear()
        self.stack_layout.setCurrentIndex(0)

    def update_sidebar(self, num_iterations: int, num_levels: int):
        """
        Aggiorna la struttura dell'albero in base al numero di iterazioni e livelli specificati.
        Genera i nodi gerarchici, assegna i dati agli item e attiva l'indice 1 del layout a stack (l'albero).

        Args:
            num_iterations (int): Il numero totale di iterazioni da visualizzare.
            num_levels (int): Il numero di livelli per ogni iterazione.
        """
        self.tree.clear()

        for i in range(num_iterations-1, -1, -1):
            iter_item = QTreeWidgetItem(self.tree)
            iter_item.setText(0, f"Iterazione {i}")
            iter_item.setData(0, Qt.ItemDataRole.UserRole, "iteration")
            iter_item.setIcon(0, QIcon("assets/attention_navigator/item_icons/iteration.svg"))
            
            for l in range(num_levels):
                level_item = QTreeWidgetItem(iter_item)
                level_item.setText(0, f"Livello {l}")
                level_item.setData(0, Qt.ItemDataRole.UserRole, "level")
                level_item.setIcon(0, QIcon("assets/attention_navigator/item_icons/level.svg"))
                
                level_item.setData(0, Qt.ItemDataRole.UserRole + 1, i)
                level_item.setData(0, Qt.ItemDataRole.UserRole + 2, l)

        # Passa alla visualizzazione dell'albero
        self.stack_layout.setCurrentIndex(1)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Slot interno attivato al click su un elemento dell'albero.
        Verifica se l'elemento è un 'level' ed emette il segnale 'level_clicked' con gli indici corrispondenti.

        Args:
            item (QTreeWidgetItem): L'elemento cliccato.
            column (int): L'indice della colonna cliccata.
        """
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_type == "level":
            iter_idx = item.data(0, Qt.ItemDataRole.UserRole + 1)
            lev_idx  = item.data(0, Qt.ItemDataRole.UserRole + 2)
            self.level_clicked.emit(iter_idx, lev_idx)