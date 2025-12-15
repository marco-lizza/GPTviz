from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import pyqtSignal, Qt

class Attention_navigator_widget(QTreeWidget):

    head_clicked = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__()
        
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformRowHeights(True)
        
        self.setIndentation(20) 
        
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #252526; 
                color: #cccccc; 
                border: none;
                font-size: 13px;
                outline: 0;
            }

            /* SPAZIATURA RIGHE: Qui decidiamo quanto sono distanti */
            QTreeWidget::item {
                height: 30px; /* Aumentato per dare respiro */
                padding-left: 5px; /* Spazio tra la freccia e il testo */
                border-bottom: 1px solid #2d2d30; /* Opzionale: riga sottile tra item */
            }

            QTreeWidget::item:selected {
                background-color: #37373d;
                color: white;
            }

            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
            /* Stile per la freccina di espansione */
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
            image: none; /* Qui potresti mettere un'icona personalizzata */
            }
        """)
        
        self.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item, column):
        """
        Gestisce il click. 
        """
        # UserRole è una costante standard per dati custom
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_type == "head":
            iter_idx = item.data(0, Qt.ItemDataRole.UserRole + 1)
            lev_idx  = item.data(0, Qt.ItemDataRole.UserRole + 2)
            head_idx = item.data(0, Qt.ItemDataRole.UserRole + 3)
            
            self.head_clicked.emit(iter_idx, lev_idx, head_idx)

    def update_sidebar(self, num_iterations,num_levels,num_heads):
        self.clear()
        
        # --- Livello 1: Iterazioni ---
        for i in range(num_iterations):
            iter_item = QTreeWidgetItem(self)
            iter_item.setText(0, f"Iterazione {i}")
            iter_item.setData(0, Qt.ItemDataRole.UserRole, "iteration")
            
            # --- Livello 2: Livelli (Layer) ---
            for l in range(num_levels):
                level_item = QTreeWidgetItem(iter_item)
                level_item.setText(0, f"Livello {l}")
                level_item.setData(0, Qt.ItemDataRole.UserRole, "level")
                
                # --- Livello 3: Heads ---
                for h in range(num_heads):
                    head_item = QTreeWidgetItem(level_item)
                    head_item.setText(0, f"Head {h}")
                    
                    # Salviamo i metadati importanti in questo item
                    # Così quando ci clicchiamo sopra, sappiamo esattamente cosa caricare
                    head_item.setData(0, Qt.ItemDataRole.UserRole, "head")
                    head_item.setData(0, Qt.ItemDataRole.UserRole + 1, i)
                    head_item.setData(0, Qt.ItemDataRole.UserRole + 2, l)
                    head_item.setData(0, Qt.ItemDataRole.UserRole + 3, h)