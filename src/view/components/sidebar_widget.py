from PyQt6.QtWidgets import QListWidget, QAbstractItemView
from PyQt6.QtCore import pyqtSignal

class SidebarView(QListWidget):

    process_requested = pyqtSignal(str)    

    def __init__(self):
        super().__init__()
        # Stile Sidebar scura
        self.setStyleSheet("""
            QListWidget {
                background-color: #252526; 
                color: #cccccc; 
                border-right: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #111;
                color: white;
            }
        """)
        # Impostazioni opzionali (es. selezione singola)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item):
        self.process_requested.emit(item.text())
    
    def update_sidebar(self, items: list):
        self.clear()
        self.addItems(items)

        