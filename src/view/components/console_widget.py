from PyQt6.QtWidgets import QTextEdit

class ConsoleView(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        # Stile "Matrix" / Terminale
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: Arial; 
                border-top: 2px solid #333;
            }
        """)

    def append_log(self, text):
        """Metodo pubblico per aggiungere testo formattato"""
        self.append(f">> {text}")

    def clear_console(self):
        self.clear()