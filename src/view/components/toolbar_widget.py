from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction 
from PyQt6.QtWidgets import QToolBar

class Toolbar(QToolBar):

    load_file_names = pyqtSignal()
    clear_console = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setMovable(False) # Blocca la toolbar in alto

        btn_load= QAction("Ricarica Workspace", self)
        btn_load.setStatusTip("Visualizza i file presenti nel workspace")
        btn_load.triggered.connect(lambda: self.load_file_names.emit())
        self.addAction(btn_load)

        #self.addSeparator()