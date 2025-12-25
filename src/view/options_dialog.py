from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class OptionsDialog(QDialog):
    """
    Finestra di dialogo modale per la configurazione delle impostazioni avanzate.

    Questa classe eredita da `QDialog` e fornisce un'interfaccia separata 
    dalla finestra principale per modificare parametri che non richiedono 
    un accesso immediato (es. configurazione temi, path, ecc.).

    Essendo un dialog, è progettata per essere eseguita con `.exec()`, 
    bloccando l'interazione con la finestra sottostante finché non viene chiusa.

    CLASSE PROVVISORIA
    """

    def __init__(self, parent=None):
        """
        Inizializza il dialog e costruisce il layout interno.

        Args:
            parent (QWidget, optional): Il widget genitore (MainWindow). 
        """
        super().__init__(parent)
        self.setWindowTitle("Impostazioni Avanzate")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Qui puoi mettere slider, form e altre impostazioni."))
        
        btn_chiudi = QPushButton("Chiudi")
        
        # self.accept è uno slot nativo di QDialog che chiude la finestra 
        # e restituisce QDialog.DialogCode.Accepted a chi l'ha chiamata.
        btn_chiudi.clicked.connect(self.accept) 
        
        layout.addWidget(btn_chiudi)
        
        self.setLayout(layout)