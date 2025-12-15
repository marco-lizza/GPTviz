from PyQt6.QtWidgets import QListWidget, QAbstractItemView
from PyQt6.QtCore import pyqtSignal

class SidebarView(QListWidget):

    file_clicked = pyqtSignal(str)    

    def __init__(self):
        super().__init__()
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
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.itemClicked.connect(self._on_file_clicked)

    def _on_file_clicked(self, item):
        self.file_clicked.emit(item.text())
    
    def update_sidebar(self, items: list):
        self.clear()
        self.addItems(items)

        