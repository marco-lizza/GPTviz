from PyQt6.QtWidgets import QMainWindow, QSplitter, QToolBar,QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from .options_dialog import options_dialog

from .components.console_widget import ConsoleView
from .components.sidebar_widget import SidebarView
from .components.workspace_widget import WorkspaceView
from .components.menu_widget import TopMenuBar
from .components.toolbar_widget import Toolbar
from .components.attentions_navigator_widget import Attention_navigator_widget

class MainWindow(QMainWindow):

    import_requested = pyqtSignal()                

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GPTviz")
        self.resize(1024, 768)

        #INIZIALIZZO I COMPONENTI
        self.console = ConsoleView()
        self.sidebar = SidebarView()
        self.attention_navigator = Attention_navigator_widget()
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

        # Splitter Sinistro (Sidebar | Attention Navigator) ---
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.addWidget(self.sidebar)
        self.h_splitter.addWidget(self.attention_navigator)

        self.h_splitter.setCollapsible(0, False)
        self.h_splitter.setCollapsible(1, False)
        
        # Facciamo 50% e 50% all'interno
        self.h_splitter.setStretchFactor(0, 1)
        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setSizes([150, 150])


        # Splitter Principale Orizzontale (Pannello Sinistro | Workspace)
        self.h1_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h1_splitter.addWidget(self.h_splitter) 
        self.h1_splitter.addWidget(self.workspace)
        
        self.h1_splitter.setCollapsible(0, False)
        self.h1_splitter.setCollapsible(1, False)

        # IMPOSTAZIONE PROPORZIONI
        
        # Quando allargo la finestra, il workspace cresce il doppio del pannello sinistro
        self.h1_splitter.setStretchFactor(0, 1) # Peso 1 (1/3 del totale)
        self.h1_splitter.setStretchFactor(1, 2) # Peso 2 (2/3 del totale)

        self.h1_splitter.setSizes([341, 683]) 

        # Splitter Verticale (Tutto il sopra | Console)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h1_splitter)
        self.v_splitter.addWidget(self.console)
        
        self.v_splitter.setCollapsible(0, False)
        self.v_splitter.setCollapsible(1, False)
        
        self.v_splitter.setStretchFactor(0, 1)
        self.v_splitter.setStretchFactor(1, 0) 
        self.v_splitter.setSizes([600, 168])

        self.setCentralWidget(self.v_splitter)

    def open_options_dialog(self):
        dialog = options_dialog(self)
        dialog.exec()