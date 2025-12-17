from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class TokenAttentionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Placeholder content
        lbl = QLabel("Qui verrà visualizzata l'attenzione sui token")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #888; font-style: italic;")
        self.layout.addWidget(lbl)

    def update_data(self, attention_tensor):
        """
        Metodo predisposto per ricevere dati in futuro.
        """
        # Qui implementerai la logica per visualizzare i token
        pass