from .toolbar_controller import Tooolbar_controller
from .sidebar_controller import Sidebar_controller
from .console_controller import Console_controller
from .workspace_controller import Workspace_controller
from .attention_navigator_controller import Attention_navigator_controller

from ..model.app_model import AppModel
from ..view.main_window import MainWindow

class AppController:
    """
    Controller principale dell'applicazione (Main Controller).

    La classe funge da punto di ingresso per la logica dell'applicazione.
    Ha la responsabilità di orchestrare la comunicazione tra il Modello (dati)
    e la Vista (interfaccia utente), oltre a inizializzare e gestire tutti i
    sotto-controller specifici per le varie aree della UI.

    Attributes:
        model (AppModel): Riferimento all'istanza del modello dati principale.
        view (MainWindow): Riferimento all'istanza della vista principale.
        toolbar_ctrl (Tooolbar_controller): Gestisce la logica della toolbar in alto.
        sidebar_ctrl (Sidebar_controller): Gestisce la logica della barra laterale.
        console_ctrl (Console_controller): Gestisce la logica della console integrata.
        workspace_ctrl (Workspace_controller): Gestisce l'area di lavoro principale.
        attention_navigator_ctrl (Attention_navigator_controller): Gestisce il navigatore dell'attenzione.
    """

    def __init__(self, model:AppModel, view:MainWindow):
        """
        Inizializza il controller principale, istanzia i sotto-controller e configura i binding.
        """
        self.model = model
        self.view = view

        # Inizializzazione dei sotto-controller
        self.toolbar_ctrl = Tooolbar_controller(model, view.toolbar)
        self.sidebar_ctrl = Sidebar_controller(model, view.sidebar)
        self.console_ctrl = Console_controller(model, view.console)
        self.workspace_ctrl = Workspace_controller(model, view.workspace)
        self.attention_navigator_ctrl = Attention_navigator_controller(model, view.attention_navigator)
        
        # Configurazione eventi e stato iniziale
        self.set_up_binding()
        self.initialize()

    def set_up_binding(self):
        """
        Collega gli eventi specifici del modello (es. richieste di apertura finestre)
        alle funzioni corrispondenti nella vista.
        """
        pass
        
    def initialize(self):
        """
        Il metodo viene utilizzato per caricare i dati iniziali necessari
        all'applicazione appena i controller sono pronti (es. caricamento lista file).
        """
        self.model.load_file_names()