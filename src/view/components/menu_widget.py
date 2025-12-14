from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction ,QKeySequence
from PyQt6.QtCore import pyqtSignal

class TopMenuBar(QMenuBar):

    open_options = pyqtSignal()
    action_exit = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # ... (Qui c'era il tuo codice per il menu File) ...
        self.setup_file_menu() # Ipotizzando tu abbia spostato il codice File qui
        
        # --- MENU OPZIONI ---
        options_menu = self.addMenu("Opzioni")

        # -- Checkbox 1: Esempio "Mostra Griglia"
        self.action_grid = QAction("Mostra Griglia", self)
        self.action_grid.setCheckable(True)  # <--- Questo crea la checkbox
        self.action_grid.setChecked(True)    # <--- Imposta il default a "Attivo"
        self.action_grid.triggered.connect(self.toggle_grid)
        options_menu.addAction(self.action_grid)

        # -- Checkbox 2: Esempio "Aggiornamento Automatico"
        self.action_auto_update = QAction("Aggiornamento Automatico", self)
        self.action_auto_update.setCheckable(True)
        self.action_auto_update.setChecked(False) # Default spento
        self.action_auto_update.triggered.connect(self.toggle_update)
        options_menu.addAction(self.action_auto_update)

        options_menu.addSeparator()

        # -- Voce "Altro..." che apre la finestra
        action_other = QAction("Altro...", self)
        action_other.triggered.connect(self.open_options.emit)
        options_menu.addAction(action_other)

    # --- Metodi di gestione (Handlers) ---

    def setup_file_menu(self):
# --- MENU FILE ---
        file_menu = self.addMenu("File")

        # 1. Apri (Standard) -> Cmd+O
        action_open = QAction("Apri...", self)
        action_open.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(action_open)

        # 2. Salva (Standard) -> Cmd+S
        action_save = QAction("Salva", self)
        action_save.setShortcut(QKeySequence.StandardKey.Save)
        file_menu.addAction(action_save)

        # 3. Salva come... (Standard) -> Shift+Cmd+S
        # Qt gestisce in automatico la combinazione corretta per Mac
        action_save_as = QAction("Salva come...", self)
        action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        file_menu.addAction(action_save_as)

        file_menu.addSeparator() # Una linea per separare i gruppi

        # 4. Importa (Custom) -> Cmd+I
        # Usiamo "Ctrl+I": su Mac Qt lo trasforma automaticamente in "Cmd+I"
        action_import = QAction("Importa...", self)
        action_import.setShortcut("Ctrl+I")
        file_menu.addAction(action_import)

        # 5. Esporta (Custom) -> Cmd+E
        action_export = QAction("Esporta...", self)
        action_export.setShortcut("Ctrl+E")
        file_menu.addAction(action_export)

        file_menu.addSeparator()

        # 6. Esci (Standard) -> Cmd+Q
        action_exit = QAction("Esci", self)
        action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        # Importante su Mac per evitare che sparisca o finisca nel menu App
        action_exit.setMenuRole(QAction.MenuRole.NoRole) 
        #action_exit.triggered.connect(self.handle_exit)
        file_menu.addAction(action_exit)

    def toggle_grid(self, checked):
        # 'checked' è un booleano (True/False)
        state = "ATTIVA" if checked else "DISATTIVA"
        print(f"Griglia {state}")
        # Qui chiameresti una funzione della tua app per nascondere/mostrare la griglia

    def toggle_update(self, checked):
        print(f"Aggiornamento automatico: {checked}")

    def cliccato_nuovo(self):
        print("Hai cliccato su Nuovo!")
        QMessageBox.information(self, "Menu", "Hai cliccato su Nuovo")