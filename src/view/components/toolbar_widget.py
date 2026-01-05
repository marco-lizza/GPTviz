from PyQt6.QtWidgets import QToolBar,QWidget,QSizePolicy
from PyQt6.QtGui import QAction,QIcon
from PyQt6.QtCore import pyqtSignal,QSize

from src.config import settings

class Toolbar(QToolBar):
    """
    Gestisce la barra dei menu superiore dell'applicazione.

    Questa classe definisce la struttura della toolbar superiore
    e le relative azioni. Non esegue logica di business diretta, ma emette segnali
    quando l'utente clicca su una voce, delegando l'azione al Controller.

    Signals:
        action_exit (None): Emesso quando si richiede la chiusura.
        clear_console (None): Emesso quando si clicca su "Clean console".
        load_file_names (None): Emesso per ricaricare la lista file nel workspace.
        import_requested(None): Emesso quando vogliamo importare un file nel workspace
    """

    action_exit = pyqtSignal()
    clear_console = pyqtSignal()
    load_file_names = pyqtSignal()
    import_requested = pyqtSignal()     

    def __init__(self,parent=None):
        """
        Configura la barra degli strumenti superiore (Toolbar).
        Aggiunge azioni rapide come Import, Opzioni ed Exit.
        """
        super().__init__("Main Toolbar")
        self.parent=parent
        self.setIconSize(QSize(settings.ICON_SIZE, settings.ICON_SIZE))
        self.setMovable(False) 
        self.setStyleSheet(settings.get_stylesheet("QToolbar_style.qss"))

        self.init_toolbar_component()

    def init_toolbar_component(self):

        """
        Azioni incluse:
            * **Import...** (Ctrl+I): Placeholder per importazione dati ( DA DEFINIRE)
            * **Reload workspace...** (Ctrl+R): Emette `load_file_names` per aggiornare la sidebar.
            * **Clean console** (Ctrl+C): Emette `clear_console` per pulire la console.
            * **Exit** (Ctrl+E): Chiude l'app
        """

        # Azione 1: Import Data
        icon_import =  QIcon("assets/utility/import.svg")
        action_import = QAction(icon_import, "Import Data", self)
        action_import.setStatusTip("Import a new file .arrow")
        action_import.setShortcut("Ctrl+I") 
        action_import.triggered.connect(self.import_requested.emit)
        self.addAction(action_import)
        
        # Azione 2: Reload
        icon_reload = QIcon("assets/utility/reload.svg")
        action_reload = QAction(icon_reload, "Reload workspace", self)
        action_reload.setStatusTip("Reload workspace")
        action_reload.setShortcut("Ctrl+R") 
        action_reload.triggered.connect(self.load_file_names.emit)
        self.addAction(action_reload)

        self.addSeparator()

        # Azione 3: Clean console
        icon_clean_console = QIcon("assets/utility/trash.svg")
        clean_console = QAction(icon_clean_console, "Clean console", self)
        clean_console.setStatusTip("Clean console")
        clean_console.setShortcut("Ctrl+C") 
        clean_console.triggered.connect(self.clear_console.emit)
        self.addAction(clean_console)

        # Spacer (Widget vuoto che si espande) per spingere le icone successive a destra
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # Azione 3: Exit (a destra)
        icon_exit =  QIcon("assets/utility/close.svg")
        action_exit = QAction(icon_exit, "Exit", self)
        action_exit.setShortcut("Ctrl+E") 
        action_exit.triggered.connect(self.action_exit.emit)
        self.addAction(action_exit)
