from PyQt6.QtWidgets import (QMainWindow, QSplitter, QStatusBar, 
                             QLabel)
from PyQt6.QtCore import Qt

from .main_window_components.console_widget import ConsoleView
from .main_window_components.sidebar_widget import SidebarView
from .main_window_components.workspace_widget.workspace_widget import WorkspaceView
from .main_window_components.toolbar_widget import Toolbar
from .main_window_components.attentions_navigator_widget import Attention_navigator_widget

from src.config import settings

class MainWindow(QMainWindow):
    """
    Finestra principale dell'applicazione (Main View).

    Questa classe assembla tutti i componenti dell'interfaccia utente in un layout
    flessibile basato su pannelli ridimensionabili (Splitters).
    Espone pubblicamente i riferimenti ai sotto-componenti (come `console`, `sidebar`)
    per permettere al Controller di collegare facilmente la logica di business.

    Struttura del Layout:
    +-----------------------------------------+
    |                Toolbar                  |
    +---------+-------------------------------+
    |         |  Attention Nav |  Workspace   |
    | Sidebar | (h1_splitter)  |              |
    |         +----------------+--------------+
    |         |            Console            |
    +---------+-------------------------------+
    |               StatusBar                 |
    +-----------------------------------------+

    Attributes:
        console (ConsoleView): Widget per i log di sistema (in basso).
        sidebar (SidebarView): Widget per la lista dei file (a sinistra).
        attention_navigator (Attention_navigator_widget): Pannello di navigazione teste (centro-sinistra).
        workspace (WorkspaceView): Area principale di visualizzazione grafici (centro-destra).
        toolbar (QToolBar): Barra degli strumenti con azioni rapide.
        statusbar (QStatusBar): Barra inferiore per messaggi e versione.
    """           

    def __init__(self):
        """
        Inizializza la finestra, i componenti figli e configura il layout.
        """
        super().__init__()

        self.setWindowTitle("GPTviz")
        self.resize(1333, 1000)

        # INIZIALIZZO I COMPONENTI
        # Questi attributi sono pubblici e verranno letti dall'AppController
        self.console = ConsoleView()
        self.sidebar = SidebarView()
        self.attention_navigator = Attention_navigator_widget()
        self.workspace = WorkspaceView()
        
        self.toolbar = Toolbar(self)
        self.toolbar.action_exit.connect(self.close)

        # Configurazione Toolbar e Statusbar
        self.addToolBar(self.toolbar)
        self._setup_statusbar()

        # Setup layout della window (Central Widget)
        self._setup_layout()
        self.center_on_screen()

    def _setup_statusbar(self):
        """
        Configura la barra di stato inferiore (StatusBar).
        Mostra messaggi temporanei a sinistra e info permanenti (Versione) a destra.
        """
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Widget permanenti (allineati a destra)
        # Etichetta Versione
        self.lbl_version = QLabel("Ver: 0.1.0-alpha")
        self.lbl_version.setStyleSheet("color: gray;")
        self.statusbar.addPermanentWidget(self.lbl_version)

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

    def center_on_screen(self):
        """
        Centra la finestra rispetto allo schermo disponibile (escludendo taskbar/dock).
        """
        # 1. Ottieni la geometria dello schermo corrente (dove apparirà la finestra)
        screen = self.screen()
        
        # availableGeometry() restituisce l'area utilizzabile (esclusa barra delle applicazioni)
        screen_geometry = screen.availableGeometry()
        
        # 2. Ottieni la geometria del rettangolo della tua finestra
        # frameGeometry() include anche la barra del titolo e i bordi
        window_geometry = self.frameGeometry()
        
        # 3. Sposta il centro logico del rettangolo della finestra 
        # al centro del rettangolo dello schermo
        window_geometry.moveCenter(screen_geometry.center())
        
        # 4. Muovi fisicamente la finestra all'angolo in alto a sinistra 
        # calcolato nel passaggio precedente
        self.move(window_geometry.topLeft())