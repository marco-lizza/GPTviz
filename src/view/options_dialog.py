from PyQt6.QtWidgets import QMenuBar, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QAction

# 1. Definiamo la finestra dedicata per le opzioni "Altro..."
class options_dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni Avanzate")
        self.resize(300, 200)
        
        # Un layout semplice per mostrare che è una finestra vera
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Qui puoi mettere slider, form e altre impostazioni."))
        
        btn_chiudi = QPushButton("Chiudi")
        btn_chiudi.clicked.connect(self.accept) # Chiude la finestra
        layout.addWidget(btn_chiudi)
        
        self.setLayout(layout)