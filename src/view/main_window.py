from PyQt6.QtWidgets import QMainWindow, QSplitter, QToolBar
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

# --- NUOVE IMPORTAZIONI MODULARI ---
# Nota: stiamo usando percorsi relativi (.) per navigare nella cartella components
from .components.console_widget import ConsoleView
from .components.sidebar_widget import SidebarView
from .components.workspace_widget import WorkspaceView

class MainWindow(QMainWindow):
    # Segnali per il Controller (nessun cambiamento qui, il contratto resta uguale)
    import_requested = pyqtSignal()            
    process_requested = pyqtSignal(str)        

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPTviz")
        self.resize(1024, 768)

        # 1. Inizializza i componenti (importati dai file separati)
        self.console = ConsoleView()
        self.sidebar = SidebarView()
        self.workspace = WorkspaceView()

        # 2. Setup UI
        self._setup_toolbar()
        self._setup_layout() # Ho estratto il layout in un metodo privato per pulizia

        # 3. Connessioni Eventi UI
        self.sidebar.itemClicked.connect(self._on_item_clicked)

    def _setup_layout(self):
        """Organizza i widget usando QSplitter"""
        
        # Splitter Orizzontale (Sidebar | Workspace)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.addWidget(self.sidebar)
        self.h_splitter.addWidget(self.workspace)
        
        # Configurazione proporzioni (Sidebar piccola, Workspace grande)
        self.h_splitter.setCollapsible(0, False) # Evita che la sidebar sparisca del tutto
        self.h_splitter.setCollapsible(1, False)
        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setSizes([250, 774]) 

        # Splitter Verticale (Contenuto | Console)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.console)
        
        # Configurazione proporzioni
        self.v_splitter.setCollapsible(0, False)
        self.v_splitter.setCollapsible(1, False) # Evita che la console sparisca
        self.v_splitter.setSizes([600, 168])

        self.setCentralWidget(self.v_splitter)

    def _setup_toolbar(self):
        toolbar = QToolBar("Toolbar Principale")
        toolbar.setMovable(False) # Blocca la toolbar in alto
        self.addToolBar(toolbar)

        # Azione Importa
        btn_import = QAction("Importa", self)
        btn_import.setStatusTip("Importa un nuovo file dati")
        # Lambda per emettere il segnale custom senza parametri extra
        btn_import.triggered.connect(lambda: self.import_requested.emit())
        toolbar.addAction(btn_import)

        toolbar.addSeparator()

        # Azione Pulisci Console (Logica UI locale, non serve disturbare il controller)
        btn_clear = QAction("Clear Log", self)
        btn_clear.triggered.connect(self.console.clear)
        toolbar.addAction(btn_clear)

    def _on_item_clicked(self, item):
        # Inoltra l'evento al Controller tramite segnale custom
        self.process_requested.emit(item.text())

    # --- API Pubblica per il Controller ---
    # Questi metodi permettono al Controller di modificare la vista 
    # senza dover conoscere i dettagli interni (es. non deve sapere che la console è un QTextEdit)
    
    def update_sidebar(self, items: list):
        self.sidebar.clear()
        self.sidebar.addItems(items)

    def update_console(self, message: str):
        self.console.append_log(message)

    def update_workspace(self, result_text: str):
        self.workspace.show_result(result_text)