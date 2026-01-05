from PyQt6.QtWidgets import QMainWindow, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal

from .options_dialog import OptionsDialog

from .components.console_widget import ConsoleView
from .components.sidebar_widget import SidebarView
from .components.workspace_widget import WorkspaceView
from .components.menu_widget import TopMenuBar
from .components.attentions_navigator_widget import Attention_navigator_widget

from src.config import settings

class MainWindow(QMainWindow):
    """
    Finestra principale dell'applicazione (Main View).

    Questa classe assembla tutti i componenti dell'interfaccia utente in un layout
    flessibile basato su pannelli ridimensionabili (Splitters).
    Espone pubblicamente i riferimenti ai sotto-componenti (come `console`, `sidebar`)
    per permettere al Controller di collegare facilmente la logica di business.

    Struttura del Layout:
    +---------+-------------------------------+
    |         |  Attention Nav |  Workspace   |
    | Sidebar | (h1_splitter)  |              |
    |         +----------------+--------------+
    |         |            Console            |
    +---------+-------------------------------+

    Attributes:
        console (ConsoleView): Widget per i log di sistema (in basso).
        sidebar (SidebarView): Widget per la lista dei file (a sinistra).
        attention_navigator (Attention_navigator_widget): Pannello di navigazione teste (centro-sinistra).
        workspace (WorkspaceView): Area principale di visualizzazione grafici (centro-destra).
        top_menu (TopMenuBar): Barra dei menu superiore.
    """

    import_requested = pyqtSignal()                

    def __init__(self):
        """
        Inizializza la finestra, i componenti figli e configura il layout.
        """
        super().__init__()

        self.setWindowTitle("GPTviz")
        self.resize(1024, 768)

        # INIZIALIZZO I COMPONENTI
        # Questi attributi sono pubblici e verranno letti dall'AppController
        self.console = ConsoleView()
        self.sidebar = SidebarView()
        self.attention_navigator = Attention_navigator_widget()
        self.workspace = WorkspaceView()
        self.top_menu = TopMenuBar()

        # Associo il menu alla window
        self.setMenuBar(self.top_menu)

        # Setup layout della window
        self._setup_layout()
        
    def _setup_layout(self):
        """
        Organizza i widget in una griglia ridimensionabile usando QSplitter nidificati.
        
        Gerarchia:
        1. `h_splitter` (Root): Divide Sidebar (sx) dal resto (dx).
        2. `v_splitter`: Divide l'area di lavoro (sopra) dalla Console (sotto).
        3. `h1_splitter`: Divide il Navigatore (sx) dal Workspace grafico (dx).
        """

        # 1. Splitter Interno Orizzontale (Navigator | Workspace)
        self.h1_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h1_splitter.addWidget(self.attention_navigator) 
        self.h1_splitter.addWidget(self.workspace)

        self.h1_splitter.setHandleWidth(5)
        self.h1_splitter.setStyleSheet(settings.get_stylesheet("QSplitter_style.qss"))
        
        self.h1_splitter.setCollapsible(0, False)
        self.h1_splitter.setCollapsible(1, False)

        # IMPOSTAZIONE PROPORZIONI
        # Quando allargo la finestra, il workspace cresce il doppio del pannello sinistro
        self.h1_splitter.setStretchFactor(0, 1) # Peso 1 (1/3 del totale)
        self.h1_splitter.setStretchFactor(1, 2) # Peso 2 (2/3 del totale)
        self.h1_splitter.setSizes([341, 683]) 

        # 2. Splitter Verticale (Area Lavoro | Console)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.setHandleWidth(5)
        self.v_splitter.setStyleSheet(settings.get_stylesheet("QSplitter_style.qss"))
        self.v_splitter.addWidget(self.h1_splitter)
        self.v_splitter.addWidget(self.console)
        
        self.v_splitter.setCollapsible(0, False)
        self.v_splitter.setCollapsible(1, False)
        
        self.v_splitter.setStretchFactor(0, 1) # Priorità all'area di lavoro
        self.v_splitter.setStretchFactor(1, 0) # La console non cresce troppo
        self.v_splitter.setSizes([600, 168])

        # 3. Splitter Principale Root (Sidebar | Area Destra)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.addWidget(self.sidebar)
        self.h_splitter.setHandleWidth(5)
        self.h_splitter.setStyleSheet(settings.get_stylesheet("QSplitter_style.qss"))
        self.h_splitter.addWidget(self.v_splitter)

        self.h_splitter.setCollapsible(0, False)
        self.h_splitter.setCollapsible(1, False)
        
        # Facciamo 50% e 50% inizialmente, o bilanciato
        self.h_splitter.setStretchFactor(0, 1)
        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setSizes([150, 150]) 

        self.setCentralWidget(self.h_splitter)

    def open_options_dialog(self):
        """
        Apre la finestra di dialogo modale delle opzioni.
        
        Blocca l'interazione con la finestra principale finché il dialog non viene chiuso (`exec`).
        """
        dialog = OptionsDialog(self)
        dialog.exec()