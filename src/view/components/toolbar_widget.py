from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction 
from PyQt6.QtWidgets import QToolBar

class Toolbar(QToolBar):

    import_requested = pyqtSignal()
    clear_console = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setMovable(False) # Blocca la toolbar in alto

        # Azione Importa
        btn_import = QAction("Importa", self)
        btn_import.setStatusTip("Importa un nuovo file dati")
        # Lambda per emettere il segnale custom senza parametri extra
        btn_import.triggered.connect(lambda: self.import_requested.emit())
        self.addAction(btn_import)

        self.addSeparator()

        # Azione Pulisci Console (Logica UI locale, non serve disturbare il controller)
        btn_clear = QAction("Clear Log", self)
        #btn_clear.triggered.connect(self.console.clear)
        self.addAction(btn_clear)