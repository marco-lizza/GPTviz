# src/ui/toolbar.py
from PyQt6.QtWidgets import QToolBar, QToolButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class CustomNavigationToolbar(NavigationToolbar):
    """
    Toolbar di navigazione Matplotlib personalizzata.
    
    Estende la funzionalità standard permettendo di:
    - Rimuovere pulsanti non necessari (es. configurazione subplots).
    - Applicare uno stile CSS (QSS) personalizzato per un look moderno/scuro.
    - Sostituire le icone standard con icone vettoriali personalizzate.
    - Cambiare il cursore del mouse in base allo strumento selezionato (Zoom/Pan).
    """
    def __init__(self, canvas, parent, coordinates=False):
        """
        Inizializza la toolbar personalizzata.

        Args:
            canvas (FigureCanvas): Il canvas su cui opera la toolbar.
            parent (QWidget): Il widget genitore.
            coordinates (bool): Se mostrare le coordinate del mouse. Default è True.
        """
        super().__init__(canvas, parent, coordinates)
        self.canvas_widget = canvas
        
        self._remove_unwanted_buttons()
        self._apply_stylesheet()

    def _remove_unwanted_buttons(self):
        """
        Rimuove dalla toolbar le azioni non desiderate, come la configurazione 
        dei margini (Subplots) e la modifica delle curve (Customize), 
        che aprono finestre di dialogo con stile non coerente.
        """
        actions = self.actions()
        for action in actions:
            if action.text() in ['Subplots', 'Customize']:
                self.removeAction(action)

    def _apply_stylesheet(self):
        """Stile CSS scuro."""
        style = """
            QToolBar {
                background-color: #2b2b2b;
                border-top: 1px solid #444;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: #383838;
                border: 1px solid #555;
                border-radius: 4px;
                color: white;
                padding: 4px;
                width: 24px; 
                height: 24px;
            }
            QToolButton:hover {
                background-color: #505050;
                border: 1px solid #777;
            }
            QToolButton:checked {
                background-color: #4a90e2;
                border: 1px solid #4a90e2;
            }
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
                font-family: monospace;
                margin-left: 10px;
            }
        """
        self.setStyleSheet(style)

    def zoom(self, *args):
        """
        Attiva o disattiva la modalità Zoom.
        Esegue l'override del metodo base per aggiornare il cursore del mouse.
        """
        super().zoom(*args)
        self._update_view_cursor()

    def pan(self, *args):
        """
        Attiva o disattiva la modalità Pan (spostamento).
        Esegue l'override del metodo base per aggiornare il cursore del mouse.
        """
        super().pan(*args)
        self._update_view_cursor()

    def _update_view_cursor(self):
        """
        Aggiorna l'icona del cursore del mouse sul canvas in base alla modalità attiva.
        
        - Zoom attivo: Cursore a croce (CrossCursor).
        - Pan attivo: Cursore a mano aperta (OpenHandCursor).
        - Nessuno: Cursore freccia standard (ArrowCursor).
        """
        current_mode = str(self.mode)
        if 'ZOOM' in current_mode:
            self.canvas_widget.setCursor(Qt.CursorShape.CrossCursor)
        elif 'PAN' in current_mode:
            self.canvas_widget.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.canvas_widget.setCursor(Qt.CursorShape.ArrowCursor)