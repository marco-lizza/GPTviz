from PyQt6.QtWidgets import QListWidget, QAbstractItemView

class SidebarView(QListWidget):
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