from PyQt6.QtWidgets import QMainWindow, QSplitter, QToolBar,QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from .options_dialog import options_dialog

from .components.console_widget import ConsoleView
from .components.sidebar_widget import SidebarView
from .components.workspace_widget import WorkspaceView
from .components.menu_widget import TopMenuBar
from .components.toolbar_widget import Toolbar

class MainWindow(QMainWindow):

    import_requested = pyqtSignal()                

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GPTviz")
        self.resize(1024, 768)

        #INIZIALIZZO I COMPONENTI
        self.console = ConsoleView()
        self.sidebar = SidebarView()
        self.sidebar1 = SidebarView()
        self.workspace = WorkspaceView()
        self.top_menu = TopMenuBar()
        self.toolbar=Toolbar()

        #Associo il menu alla window
        self.setMenuBar(self.top_menu)

        #Associo la toolbar alla window
        self.addToolBar(self.toolbar)

        # Setup layout della window
        self._setup_layout()
        

    def _setup_layout(self):
        """Organizza i widget usando QSplitter"""

        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.addWidget(self.sidebar)
        self.h_splitter.addWidget(self.sidebar1)

        self.h_splitter.setCollapsible(0, False) # Evita che la sidebar sparisca del tutto
        self.h_splitter.setCollapsible(1, False)
        self.h_splitter.setStretchFactor(1, 1)
        
        # Splitter Orizzontale (Sidebar | Workspace)
        self.h1_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h1_splitter.addWidget(self.h_splitter)
        self.h1_splitter.addWidget(self.workspace)
        
        # Configurazione proporzioni (Sidebar piccola, Workspace grande)
        self.h1_splitter.setCollapsible(0, False) # Evita che la sidebar sparisca del tutto
        self.h1_splitter.setCollapsible(1, False)
        self.h1_splitter.setStretchFactor(1, 1)
        self.h1_splitter.setSizes([250, 774]) 

        # Splitter Verticale (Contenuto | Console)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h1_splitter)
        self.v_splitter.addWidget(self.console)
        
        # Configurazione proporzioni
        self.v_splitter.setCollapsible(0, False)
        self.v_splitter.setCollapsible(1, False) # Evita che la console sparisca
        self.v_splitter.setSizes([600, 168])

        self.setCentralWidget(self.v_splitter)

    def open_options_dialog(self):
        # La MainWindow è l'unica che sa che esiste la classe OptionsDialog
        dialog = options_dialog(self)
        dialog.exec()