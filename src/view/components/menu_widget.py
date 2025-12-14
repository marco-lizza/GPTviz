from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction ,QKeySequence
from PyQt6.QtCore import pyqtSignal

class TopMenuBar(QMenuBar):

    open_options = pyqtSignal()
    action_exit = pyqtSignal()
    clear_console = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_file_menu()
        self.setup_options_menu()
        self.setup_console_menu()

    def setup_file_menu(self):
        
        file_menu = self.addMenu("File")

        action_open = QAction("Apri...", self)
        action_open.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(action_open)

        action_save = QAction("Salva", self)
        action_save.setShortcut(QKeySequence.StandardKey.Save)
        file_menu.addAction(action_save)

        action_save_as = QAction("Salva come...", self)
        action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        file_menu.addAction(action_save_as)

        file_menu.addSeparator()

        action_import = QAction("Importa...", self)
        action_import.setShortcut("Ctrl+I")
        file_menu.addAction(action_import)

        action_export = QAction("Esporta...", self)
        action_export.setShortcut("Ctrl+E")
        file_menu.addAction(action_export)

        file_menu.addSeparator()

        action_exit = QAction("Esci", self)
        action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        action_exit.setMenuRole(QAction.MenuRole.NoRole) 
        file_menu.addAction(action_exit)

    def setup_options_menu(self):
        # --- MENU OPZIONI ---
        options_menu = self.addMenu("Opzioni")

        self.action_grid = QAction("Mostra Griglia", self)
        self.action_grid.setCheckable(True)  
        self.action_grid.setChecked(True)  
        self.action_grid.triggered.connect(self.toggle_grid)
        options_menu.addAction(self.action_grid)

        self.action_auto_update = QAction("Aggiornamento Automatico", self)
        self.action_auto_update.setCheckable(True)
        self.action_auto_update.setChecked(False)
        self.action_auto_update.triggered.connect(self.toggle_update)
        options_menu.addAction(self.action_auto_update)

        options_menu.addSeparator()

        action_other = QAction("Altro...", self)
        action_other.triggered.connect(self.open_options.emit)
        options_menu.addAction(action_other)

    def setup_console_menu(self):
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
        


    def toggle_grid(self, checked):
        state = "ATTIVA" if checked else "DISATTIVA"
        print(f"Griglia {state}")

    def toggle_update(self, checked):
        print(f"Aggiornamento automatico: {checked}")
