from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class WorkspaceView(QFrame):
    def __init__(self):
        super().__init__()
        
        # Stile dell'area di lavoro
        self.setStyleSheet("background-color: #333333;")
        
        # Layout interno
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder iniziale
        self.label = QLabel("Nessun elemento selezionato")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #666; font-size: 24px; font-weight: bold;")
        
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def show_result(self, text):
        """Aggiorna il contenuto visivo dell'area di lavoro"""
        self.label.setText(text)
        self.label.setStyleSheet("color: white; font-size: 24px;")