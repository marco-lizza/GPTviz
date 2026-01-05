from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal

class TopMenuBar(QMenuBar):
    """
    Gestisce la barra dei menu superiore dell'applicazione.

    Questa classe definisce la struttura gerarchica dei menu (GPTViz, File, Console)
    e le relative azioni. Non esegue logica di business diretta, ma emette segnali
    quando l'utente clicca su una voce, delegando l'azione al Controller.

    Signals:
        open_options (None): Emesso quando si clicca su "Preferences/Options".
        action_exit (None): Emesso quando si richiede la chiusura (non ancora collegato).
        clear_console (None): Emesso quando si clicca su "Pulisci Console".
        load_file_names (None): Emesso per ricaricare la lista file nel workspace.
    """

    open_options = pyqtSignal()
    action_exit = pyqtSignal()
    clear_console = pyqtSignal()
    load_file_names = pyqtSignal()

    def __init__(self):
        """
        Inizializza la barra dei menu e costruisce le sottosezioni.
        """
        super().__init__()
        
        self.setup_gptviz_menu()
        self.setup_file_menu()
        self.setup_console_menu()

    def setup_file_menu(self):
        """
        Configura il menu 'File'.

        Azioni incluse:
        * **Import...** (Ctrl+I): Placeholder per importazione dati ( DA DEFINIRE)
        * **Reload workspace...** (Ctrl+R): Emette `load_file_names` per aggiornare la sidebar.
        """
        # --- MENU FILE ---
        file_menu = self.addMenu("File")

        self.import_file = QAction("Import...", self)
        self.import_file.setShortcut("Ctrl+I") 
        file_menu.addAction(self.import_file)

        file_menu.addSeparator()

        self.load_files_in_workspace = QAction("Reload workspace...", self)
        self.load_files_in_workspace.setShortcut("Ctrl+R") 
        
        # Connessione del segnale
        self.load_files_in_workspace.triggered.connect(self.load_file_names.emit)
        file_menu.addAction(self.load_files_in_workspace)

    def setup_gptviz_menu(self):
        """
        Configura il menu 'GPTViz' (Menu applicazione).

        Azioni incluse:
        * **Preferences...**: Apre il dialog delle opzioni.

        """
        # --- MENU GPTviz ---
        gptviz_menu = self.addMenu("GPTViz")

        self.action_other = QAction("Preferences...", self)
        self.action_other.triggered.connect(self.open_options.emit)
        gptviz_menu.addAction(self.action_other)

    def setup_console_menu(self):
        """
        Configura il menu 'Console'.

        Azioni incluse:
        * **Pulisci Console** (Ctrl+L): Pulisce l'output della console.
        * **Salva log Console** (Ctrl+S): Placeholder per il salvataggio su file. ( DA DEFINIRE )
        """
        # --- MENU CONSOLE ---
        console_menu = self.addMenu("Console")

        self.action_clear_console = QAction("Pulisci Console", self)
        self.action_clear_console.setShortcut("Ctrl+L") 
        self.action_clear_console.triggered.connect(self.clear_console.emit)
        console_menu.addAction(self.action_clear_console)

        console_menu.addSeparator()

        self.action_save_console = QAction("Salva log Console", self)
        self.action_save_console.setShortcut("Ctrl+S") 
    
        console_menu.addAction(self.action_save_console)